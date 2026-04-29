"""
Chat service — handles conversation turns.
Switch providers by setting LLM_PROVIDER=ollama|vllm in your .env.local
"""

from pathlib import Path

from app.models.data.chat import ChatMessage
from app.models.llms.chat_model import ChatModel
from app.services.load_lessons import load_lesson
from app.services.session_store import get_session
from app.services.model_config import active_model, get_client

LESSONS_DIR = Path(__file__).parents[2] / "app" / "data" / "lessons"

sessions: dict[str, list[ChatMessage]] = {}


def handle_conversation(
    message: ChatMessage,
    lesson_id: str,
    session_id: str,
    model_id: str | None = None,
) -> list[ChatMessage]:

    session_config = get_session(session_id)
    lesson = load_lesson(lesson_path=LESSONS_DIR / f"{lesson_id}.toml")
    chat_model = ChatModel(
        session_config=session_config,
        lesson_config=lesson,
        model_id=active_model(model_id),
    )

    if session_id not in sessions:
        sessions[session_id] = [
            ChatMessage(role="system", content=chat_model.system_prompt)
        ]

    sessions[session_id].append(message)

    client, resolved_model = get_client(model_id)
    response = client.chat.completions.create(
        model=resolved_model,
        messages=[m.model_dump() for m in sessions[session_id]],
    )

    assistant = ChatMessage(
        role="assistant",
        content=response.choices[0].message.content,
    )

    sessions[session_id].append(assistant)

    return list(sessions[session_id])