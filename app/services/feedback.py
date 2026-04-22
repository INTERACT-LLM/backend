"""
Feedback service (seperate API call from chat endpoint)

Structured feedback response based on https://docs.ollama.com/capabilities/structured-outputs#python-2
-> Note: Ollama recommends passing JSON schema as prompt + in the chat call
"""
from pathlib import Path
import re
import ollama
from app.models.data.feedback import FeedbackResponse, GeneralFeedbackResponse
from app.services.load_environments import load_lesson, load_session
from app.models.llms.feedback_model import FeedbackModel
from app.services.model_config import MODEL

def generate_immediate_feedback(
    last_user_message: dict,
    lesson_id: str,
):
    session_config = load_session(session_path=Path(__file__).parents[2] / "app" / "data" / "session.toml")
    lesson = load_lesson(lesson_path=Path(__file__).parents[2] / "app" / "data" / "lessons" / f"{lesson_id}.toml")
    feedback_model = FeedbackModel(model_id=MODEL, session_config=session_config, lesson_config=lesson)

    # build system prompt
    system_prompt = feedback_model.immediate_feedback_prompt

    # messages
    messages = [{"role": "system", "content": system_prompt}] + [last_user_message]

    response = ollama.chat(
        model=feedback_model.model_id,
        messages=messages,
    )

    try:
        feedback = FeedbackResponse.model_validate_json(response.message.content)
        feedback_status = "success"
    except Exception as e:
        return {"FeedbackResponse": None, "feedback_status": "error", "detail": str(e)}

    return {"FeedbackResponse": feedback, "feedback_status": feedback_status}

def generate_general_feedback(messages: list[dict], lesson_id: str, only_user_messages: bool = False):
    """
    From conversation history, generate structured feedback with positives and improvements.
    Always returns both structured output (if possible) and raw model output.
    """
    if only_user_messages:
        messages = [m for m in messages if m["role"] == "user"]

    formatted_conversation = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in messages
    )
    session_config = load_session(session_path=Path(__file__).parents[2] / "app" / "data" / "session.toml")
    lesson = load_lesson(lesson_path=Path(__file__).parents[2] / "app" / "data" / "lessons" / f"{lesson_id}.toml")
    feedback_model = FeedbackModel(
        model_id=MODEL,
        session_config=session_config,
        lesson_config=lesson,
        conversation=formatted_conversation,
    )
    prompt = feedback_model.general_feedback_prompt

    response = ollama.chat(
        model=feedback_model.model_id,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_output = response.message.content.strip()

    feedback = None
    error = None

    # direct Pydantic parse
    try:
        feedback = GeneralFeedbackResponse.model_validate_json(raw_output)

    except Exception:
        # extract JSON block if model adds extra text
        try:
            match = re.search(r"\{.*\}", raw_output, re.DOTALL)
            if match:
                cleaned = match.group()
                feedback = GeneralFeedbackResponse.model_validate_json(cleaned)
        except Exception as e:
            error = str(e)

    
    return {
        "GeneralFeedbackResponse": feedback,
        "raw_output": raw_output,
        "error": error
    }