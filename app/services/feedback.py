"""
Feedback service (separate API call from chat endpoint)

Structured feedback response using OpenAI-compatible API (Ollama or vLLM or Anthropic).
Provider and model are inherited from the chat the feedback is generated for —
feedback uses the same provider and model (state.config.model) as the conversation it analyses.

Both feedback functions always return a dict with feedback_status "success" or "error",
so the frontend can stop loading in both cases. On error, "error" says why, and
"raw_output" holds the model's text if there was one.
"""

from pathlib import Path
import json
import re

from app.models.data.feedback import FeedbackResponse, GeneralFeedbackResponse
from app.models.llms.feedback_model import FeedbackModel
from app.services.load_lessons import load_lesson
from app.services.model_config import get_client
from app.services.store_interactions.store_chat import get_chat

LESSONS_DIR = Path(__file__).parents[2] / "app" / "data" / "lessons"

# characters that may follow a backslash inside a JSON string (\u is checked separately)
_VALID_ESCAPES = set('"\\/bfnrt')

# a backslash plus either a full unicode escape (\u + 4 hex digits) or one character
_ESCAPE_PAIR = re.compile(r"\\(u[0-9a-fA-F]{4}|.)", re.DOTALL)

# reads one JSON object and stops; strict=False allows line breaks inside strings
_DECODER = json.JSONDecoder(strict=False)


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
        config=state.config,
        lesson_config=lesson_config,
        **kwargs,
    )
    return feedback_model, state


def _fix_invalid_escapes(text: str) -> str:
    """
    Remove backslashes JSON does not allow, e.g. \\' becomes ' and \\u23 becomes u23.
    Works on pairs, so a valid escaped backslash (\\\\) and a full \\u00e9 are kept as they are.
    """
    def fix(match: re.Match) -> str:
        escaped = match.group(1)
        if len(escaped) == 5 or escaped in _VALID_ESCAPES:  # \uXXXX or a valid single escape
            return match.group(0)
        return escaped  # drop the backslash, keep the character

    return _ESCAPE_PAIR.sub(fix, text)


def _first_json_object(text: str) -> dict:
    """
    Read the first complete JSON object in text and ignore whatever comes after it.
    Handles clean JSON, JSON wrapped in other text, and trailing junk like an extra }.
    """
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in model output")
    obj, _end = _DECODER.raw_decode(text, start)
    return obj


def _parse_json_response(raw: str | None, model_cls):
    """
    Try to turn the model's text into model_cls.
    Returns (parsed, None) on success, (None, error message) on failure. Never raises.

    Tries the text as it is first, then once more with invalid backslashes removed,
    so well-formed answers are never changed.
    """
    if not raw:
        return None, "Model returned an empty response"

    last_error = "No valid JSON found in model output"
    for attempt in (raw, _fix_invalid_escapes(raw)):
        try:
            return model_cls.model_validate(_first_json_object(attempt)), None
        except Exception as e:
            last_error = str(e)
    return None, last_error


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

    client, _ = get_client(state.config.provider)
    try:
        response = client.chat.completions.create(model=state.config.model, messages=messages)
    except Exception as e:
        return {
            "FeedbackResponse": None,
            "feedback_status": "error",
            "raw_output": None,
            "error": f"Provider unavailable: {type(e).__name__}: {e}",
        }

    raw_output = response.choices[0].message.content  # may be None, the parser handles it
    feedback, error = _parse_json_response(raw_output, FeedbackResponse)

    return {
        "FeedbackResponse": feedback,
        "feedback_status": "error" if error else "success",
        "raw_output": raw_output,
        "error": error,
    }


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

    client, _ = get_client(state.config.provider)
    try:
        response = client.chat.completions.create(
            model=state.config.model,
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