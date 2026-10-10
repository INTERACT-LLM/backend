"""
Feedback service (separate API call from chat endpoint)

Structured feedback response using OpenAI-compatible API (Ollama or vLLM or Anthropic).
Provider and model are inherited from the chat the feedback is generated for —
feedback uses the same provider as the conversation it analyses.

Both feedback functions always return a dict with feedback_status "success" or "error",
so the frontend can stop loading in both cases.
"""

from pathlib import Path
import re

from app.models.data.feedback import FeedbackResponse, GeneralFeedbackResponse
from app.models.llms.feedback_model import FeedbackModel
from app.services.load_lessons import load_lesson
from app.services.model_config import get_client
from app.services.store_interactions.store_chat import get_chat

LESSONS_DIR = Path(__file__).parents[2] / "app" / "data" / "lessons"


def _load_feedback_model(
    lesson_id: str | None,
    chat_id: str,
    **kwargs,
):
    """
    Shared setup. Returns (feedback_model, state) so callers can read
    state.config.provider and state.config.model for the LLM call.
    """
    state = get_chat(chat_id)
    if not state:
        raise ValueError(f"Chat not found: {chat_id}")

    lesson_config = (
        load_lesson(lesson_path=LESSONS_DIR / f"{lesson_id}.toml")
        if lesson_id
        else None
    )

    feedback_model = FeedbackModel(
        model_id=state.config.model,  
        config=state.config,  
        lesson_config=lesson_config,
        **kwargs,
    )
    return feedback_model, state


def _parse_json_response(raw: str | None, model_cls):
    """
    Try to turn the model's text into model_cls.
    Returns (parsed, None) on success, (None, error message) on failure. Never raises.
    """
    if not raw:
        return None, "Model returned an empty response"

    # 1. the whole output is valid JSON
    try:
        return model_cls.model_validate_json(raw), None
    except Exception:
        pass

    # 2. JSON is wrapped in other text, e.g. ```json ... ``` or a sentence before it
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None, "No valid JSON found in model output"
    try:
        return model_cls.model_validate_json(match.group()), None
    except Exception as e:
        return None, str(e)


def generate_immediate_feedback(
    last_user_message: dict,
    lesson_id: str | None,
    chat_id: str,
):
    feedback_model, state = _load_feedback_model(lesson_id, chat_id)

    # Only role and content go to the LLM, never our bookkeeping fields (id, synthetic).
    llm_user_message = {
        "role": last_user_message["role"],
        "content": last_user_message["content"],
    }

    messages = [
        {"role": "system", "content": feedback_model.immediate_feedback_prompt},
        llm_user_message,
    ]

    client, resolved_model = get_client(state.config.provider)  
    try:
        response = client.chat.completions.create(model=resolved_model, messages=messages)
    except Exception as e:
        return {
            "FeedbackResponse": None,
            "feedback_status": "error",
            "detail": f"Provider unavailable: {type(e).__name__}: {e}",
        }

    raw_output = response.choices[0].message.content  # may be None, the parser handles it
    feedback, error = _parse_json_response(raw_output, FeedbackResponse)
    if error:
        return {"FeedbackResponse": None, "feedback_status": "error", "detail": error}
    return {"FeedbackResponse": feedback, "feedback_status": "success"}


def generate_general_feedback(
    messages: list[dict],
    lesson_id: str | None,
    chat_id: str,
    only_user_messages: bool = False,
):
    messages = [
        m for m in messages
        if not m.get("synthetic", False) and m.get("role") != "system"
    ]

    if only_user_messages:
        messages = [m for m in messages if m["role"] == "user"]

    formatted_conversation = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in messages
    )

    feedback_model, state = _load_feedback_model(
        lesson_id, chat_id, conversation=formatted_conversation
    )

    print(f"general_feedback_prompt:\n{feedback_model.general_feedback_prompt}")

    client, resolved_model = get_client(state.config.provider)  
    try:
        response = client.chat.completions.create(
            model=resolved_model,
            messages=[{"role": "user", "content": feedback_model.general_feedback_prompt}],
        )
    except Exception as e:
        return {
            "GeneralFeedbackResponse": None,
            "feedback_status": "error",
            "raw_output": None,
            "error": f"Provider unavailable: {type(e).__name__}: {e}",
        }

    # content can be None, so fall back to "" before strip()
    raw_output = (response.choices[0].message.content or "").strip()
    feedback, error = _parse_json_response(raw_output, GeneralFeedbackResponse)

    print(f"general_feedback raw_output:\n{raw_output}\nparse error: {error}")

    return {
        "GeneralFeedbackResponse": feedback,
        "feedback_status": "error" if error else "success",
        "raw_output": raw_output,
        "error": error,
    }