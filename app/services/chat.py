"""
Chat service — handles message turns and streaming.
History is stored in ChatState via store_chat.
System prompt is built once from the chat's frozen config.

Provider and model are bound to the chat at creation time (see ChatConfig).
If the bound provider fails mid-conversation, the chat is terminated; the
user must start a new chat (which will bind to whichever provider is then active).

Saving after a turn goes through _merge_latest inside chat_lock, so events logged
while the tutor was streaming (tabu guess, end reason) are never overwritten.
"""
from pathlib import Path
from collections.abc import Generator

from app.models.data.chat import ChatMessage, ChatState
from app.models.llms.chat_model import ChatModel
from app.services.load_lessons import load_lesson
from app.services.store_interactions.store_chat import get_chat, create_chat, now_local, chat_lock
from app.services.model_config import get_client
from app.services.provider_state import provider_state

LESSONS_DIR = Path(__file__).parents[2] / "app" / "data" / "lessons"

TUTOR_START_PROMPT = "Please begin the lesson. Start the conversation in the target language."

# fields that only exist for our own bookkeeping. Never sent to the LLM.
INTERNAL_FIELDS = {"synthetic", "id"}


def _build_chat_model(state: ChatState) -> ChatModel:
    """Build a ChatModel from the chat's config and lesson. Called once per chat."""
    lesson = (
        load_lesson(lesson_path=LESSONS_DIR / f"{state.config.lesson_id}.toml")
        if state.config.lesson_id
        else None
    )
    return ChatModel(
        config=state.config,
        chat_id=state.chat_id,  # seed for the 20Q secret, same as the game-state endpoint
        lesson_config=lesson,
        model_id=state.config.model,
    )


def _ensure_system_prompt(state: ChatState, chat_model: ChatModel) -> None:
    """Inject the system prompt if this is the first turn."""
    if not state.messages:
        state.messages.append(
            ChatMessage(role="system", content=chat_model.system_prompt)
        )


def _merge_latest(state: ChatState) -> ChatState:
    """
    Re-read the chat file and put this turn's messages on top of it.
    Call this inside `with chat_lock:` together with the save that follows.

    `state` was loaded before streaming started. While the tutor was answering,
    the learner may have logged an event (tabu guess, end reason) that is already
    in the file. Saving `state` directly would erase it, so we keep the file's
    version and only replace the messages, which this turn owns.
    """
    latest = get_chat(state.chat_id)
    if latest is None:
        return state
    latest.messages = state.messages
    return latest


def _terminate_on_failure(state: ChatState, exc: Exception) -> None:
    """
    Mark the chat terminated and flip ProviderState if the bound provider was primary.
    Also records provider_terminated as the end reason, unless one is already set.
    Persists the updated state.
    """
    with chat_lock:
        latest = _merge_latest(state)
        latest.status = "terminated"
        latest.terminated_reason = f"{type(exc).__name__}: {exc}"

        # first reason wins, e.g. a chat that was already user_ended stays user_ended
        if latest.ended_reason is None:
            latest.ended_reason = "provider_terminated"
            latest.ended_at = now_local()

        create_chat(latest)

    # Only flip ProviderState if this was the primary that failed.
    # Anthropic failures don't trigger failover (there's nowhere to fail over to).
    # A plain call: provider_state is thread-safe, and this runs in a worker thread.
    if state.config.provider == provider_state.primary:
        provider_state.mark_primary_failed()


def _stream_response(state: ChatState) -> Generator[str, None, None]:
    """
    Stream one assistant turn, append the result to state, and persist.
    Excludes internal fields (synthetic, id) before sending to the LLM.

    On provider failure: terminate the chat, flip ProviderState (if primary),
    yield an error event the frontend can act on.
    """
    provider = state.config.provider #read once, used below
    try:
        client, resolved_model = get_client(provider)
        stream = client.chat.completions.create(
            model=resolved_model,
            messages=[m.model_dump(exclude=INTERNAL_FIELDS) for m in state.messages],
            stream=True,
            max_tokens=400,
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
        # re-read and save as one step, so events logged during streaming survive
        with chat_lock:
            create_chat(_merge_latest(state))
        yield "data: [DONE]\n\n"

    except Exception as exc:
        print(f"[chat] Provider {provider!r} failed for chat {state.chat_id}: {exc}")
        _terminate_on_failure(state, exc)
        yield f'data: {{"error": "provider_unavailable", "provider": "{provider}"}}\n\n'
        yield "data: [DONE]\n\n"


def start_chat(chat_id: str) -> Generator[str, None, None]:
    """
    Tutor-starts flow. Called once after chat creation when tutor_starts=True.
    Injects the synthetic kickoff prompt and streams the tutor's opening turn.
    All subsequent turns go through handle_message.
    """
    state = get_chat(chat_id)
    chat_model = _build_chat_model(state)
    _ensure_system_prompt(state, chat_model)

    state.messages.append(
        ChatMessage(role="user", content=TUTOR_START_PROMPT, synthetic=True)
    )
    yield from _stream_response(state)


def handle_message(chat_id: str, message: ChatMessage) -> Generator[str, None, None]:
    """
    Normal turn. Works for both free chat and lesson chat.
    System prompt is injected on the first call if start_chat was never called.
    """
    state = get_chat(chat_id)
    chat_model = _build_chat_model(state)
    _ensure_system_prompt(state, chat_model)

    state.messages.append(message)
    yield from _stream_response(state)