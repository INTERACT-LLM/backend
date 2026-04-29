"""
Chat service — handles conversation turns.
Switch providers by setting LLM_PROVIDER=ollama|vllm in your .env.local
"""

from pathlib import Path
from collections.abc import Generator

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
) -> Generator[str, None, None]:

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
    stream = client.chat.completions.create(
        model=resolved_model,
        messages=[m.model_dump() for m in sessions[session_id]],
        stream=True,
    )

    collected: list[str] = []
    for chunk in stream:
        token = chunk.choices[0].delta.content or ""
        if token:
            collected.append(token)
            yield f"data: {token}\n\n"

    sessions[session_id].append(
        ChatMessage(role="assistant", content="".join(collected))
    )
    yield "data: [DONE]\n\n"