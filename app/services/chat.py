"""
Add minimal LLM logic here
"""

from pathlib import Path
import ollama

# models
from app.models.data.chat import ChatMessage
from app.models.llms.chat_model import ChatModel

# services
from app.services.load_lessons import load_lesson
from app.services.session_store import get_session
from app.services.model_config import MODEL

sessions = {}

def handle_conversation(
    message: ChatMessage,
    lesson_id: str,
    session_id: str,
) -> list[ChatMessage]:

    session_config = get_session(session_id)
    lesson = load_lesson(lesson_path=Path(__file__).parents[2] / "app" / "data" / "lessons" / f"{lesson_id}.toml")
    chat_model = ChatModel(session_config=session_config, lesson_config=lesson, model_id=MODEL)

    if session_id not in sessions:
        sessions[session_id] = [
            ChatMessage(role="system", content=chat_model.system_prompt)
        ]

    sessions[session_id].append(message)

    response = ollama.chat(
        model=chat_model.model_id,
        messages=[m.model_dump() for m in sessions[session_id]],
    )

    assistant = ChatMessage(
        role="assistant",
        content=response["message"]["content"]
    )

    sessions[session_id].append(assistant)

    return list(sessions[session_id])