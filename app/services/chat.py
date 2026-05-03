"""
Chat service — handles message turns and streaming.
History is stored in ChatState via store_chat.
System prompt is built once from the snapshotted session config.
"""
from pathlib import Path
from collections.abc import Generator

from app.models.data.chat import ChatMessage, ChatState
from app.models.llms.chat_model import ChatModel
from app.services.load_lessons import load_lesson
from app.services.store_chat import get_chat, create_chat
from app.services.model_config import active_model, get_client

LESSONS_DIR = Path(__file__).parents[2] / "app" / "data" / "lessons"

TUTOR_START_PROMPT = "Please begin the lesson. Start the conversation in the target language."


def _build_chat_model(state: ChatState, model_id: str | None) -> ChatModel:
    """Build a ChatModel from the snapshotted config and lesson. Called once per chat."""
    lesson = (
        load_lesson(lesson_path=LESSONS_DIR / f"{state.lesson_id}.toml")
        if state.lesson_id
        else None
    )
    return ChatModel(
        session_config=state.snapshotted_config,
        lesson_config=lesson,
        model_id=active_model(model_id),
    )


def _ensure_system_prompt(state: ChatState, chat_model: ChatModel) -> None:
    """Inject the system prompt if this is the first turn."""
    if not state.messages:
        state.messages.append(
            ChatMessage(role="system", content=chat_model.system_prompt)
        )


def _stream_response(state: ChatState, model_id: str | None) -> Generator[str, None, None]:
    """
    Stream one assistant turn, append the result to state, and persist.
    Excludes internal fields (synthetic) before sending to the LLM.
    """
    client, resolved_model = get_client(model_id)
    stream = client.chat.completions.create(
        model=resolved_model,
        messages=[m.model_dump(exclude={"synthetic"}) for m in state.messages],
        stream=True,
    )

    collected: list[str] = []
    for chunk in stream:
        token = chunk.choices[0].delta.content or ""
        if token:
            collected.append(token)
            yield f"data: {token}\n\n"

    state.messages.append(
        ChatMessage(role="assistant", content="".join(collected))
    )
    create_chat(state)
    yield "data: [DONE]\n\n"


def start_chat(
    chat_id: str,
    model_id: str | None = None,
) -> Generator[str, None, None]:
    """
    Tutor-starts flow. Called once after chat creation when tutor_starts=True.
    Injects the synthetic kickoff prompt and streams the tutor's opening turn.
    All subsequent turns go through handle_message.
    """
    state = get_chat(chat_id)
    chat_model = _build_chat_model(state, model_id)
    _ensure_system_prompt(state, chat_model)

    state.messages.append(
        ChatMessage(role="user", content=TUTOR_START_PROMPT, synthetic=True)
    )
    yield from _stream_response(state, model_id)


def handle_message(
    chat_id: str,
    message: ChatMessage,
    model_id: str | None = None,
) -> Generator[str, None, None]:
    """
    Normal turn. Works for both free chat and lesson chat.
    System prompt is injected on the first call if start_chat was never called.
    """
    state = get_chat(chat_id)
    chat_model = _build_chat_model(state, model_id)
    _ensure_system_prompt(state, chat_model)

    state.messages.append(message)
    yield from _stream_response(state, model_id)