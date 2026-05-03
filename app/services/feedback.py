"""
Feedback service (separate API call from chat endpoint)

Structured feedback response using OpenAI-compatible API (Ollama or vLLM).
"""

from pathlib import Path
import re

from app.models.data.feedback import FeedbackResponse, GeneralFeedbackResponse
from app.models.llms.feedback_model import FeedbackModel
from app.services.load_lessons import load_lesson
from app.services.model_config import active_model, get_client
from app.services.store_chat import get_chat

LESSONS_DIR = Path(__file__).parents[2] / "app" / "data" / "lessons"


def _load_feedback_model(
    lesson_id: str,
    chat_id: str,
    model_id: str | None = None,
    **kwargs,
) -> FeedbackModel:
    """Shared setup for both feedback functions."""
    state = get_chat(chat_id)
    if not state:
        raise ValueError(f"Chat not found: {chat_id}")
    return FeedbackModel(
        model_id=active_model(model_id),
        session_config=state.snapshotted_config,
        lesson_config=load_lesson(lesson_path=LESSONS_DIR / f"{lesson_id}.toml"),
        **kwargs,
    )


def _parse_json_response(raw: str, model_cls):
    """
    Try to parse raw model output into a Pydantic model.
    Falls back to extracting the first JSON block if direct parsing fails.
    Returns (instance | None, error | None).
    """
    try:
        return model_cls.model_validate_json(raw), None
    except Exception:
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return model_cls.model_validate_json(match.group()), None
        except Exception as e:
            return None, str(e)
    return None, "No valid JSON found in model output"


def generate_immediate_feedback(
    last_user_message: dict,
    lesson_id: str,
    chat_id: str,
    model_id: str | None = None,
):
    feedback_model = _load_feedback_model(lesson_id, chat_id, model_id=model_id)

    messages = [
        {"role": "system", "content": feedback_model.immediate_feedback_prompt},
        last_user_message,
    ]

    client, resolved_model = get_client(model_id)
    response = client.chat.completions.create(model=resolved_model, messages=messages)
    raw_output = response.choices[0].message.content

    feedback, error = _parse_json_response(raw_output, FeedbackResponse)
    if error:
        return {"FeedbackResponse": None, "feedback_status": "error", "detail": error}
    return {"FeedbackResponse": feedback, "feedback_status": "success"}


def generate_general_feedback(
    messages: list[dict],
    lesson_id: str,
    chat_id: str,
    model_id: str | None = None,
    only_user_messages: bool = False,
):
    """
    From conversation history, generate structured feedback with positives and improvements.
    Synthetic messages (e.g. tutor kickoff) are excluded from analysis.
    """
    # strip synthetic messages — they are internal scaffolding, not real student input
    # strip synthetic and system messages — internal scaffolding, not real student input
    messages = [
        m for m in messages
        if not m.get("synthetic", False) and m.get("role") != "system"
    ]

    if only_user_messages:
        messages = [m for m in messages if m["role"] == "user"]

    formatted_conversation = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in messages
    )

    feedback_model = _load_feedback_model(
        lesson_id, chat_id, model_id=model_id, conversation=formatted_conversation
    )

    # print the prompt for debugging
    print(f"general_feedback_prompt:\n{feedback_model.general_feedback_prompt}")

    client, resolved_model = get_client(model_id)
    response = client.chat.completions.create(
        model=resolved_model,
        messages=[{"role": "user", "content": feedback_model.general_feedback_prompt}],
    )

    raw_output = response.choices[0].message.content.strip()
    feedback, error = _parse_json_response(raw_output, GeneralFeedbackResponse)

    return {
        "GeneralFeedbackResponse": feedback,
        "raw_output": raw_output,
        "error": error,
    }