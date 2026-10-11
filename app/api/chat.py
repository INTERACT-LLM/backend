"""
Chat endpoints.
Handles chat lifecycle: creation, tutor opener, message turns, logging events, and cleanup.

Every read-change-write on a chat file happens inside `with chat_lock:`,
so two requests for the same chat can never overwrite each other (see store_chat).
"""
import random
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.models.data.chat import (
    CreateChatRequest, ChatMessageRequest, StartChatRequest,
    EndChatRequest, TabuGuessRequest,
    ChatState, ChatConfig, ChatMessage, TabuState, TabuViolation,
)
from app.models.environments.lesson import TabuInstructions
from app.models.llms.chat_model import ChatModel
from app.services.chat import start_chat, handle_message
from app.services.load_lessons import load_lesson
from app.services.model_config import settings
from app.services.provider_state import provider_state # for fallback logic
from app.services.store_interactions.store_chat import (
    create_chat, get_chat, save_chat, now_local, chat_lock,
)

router = APIRouter()

# same folder as in the lessons router
LESSONS_DIR = Path(__file__).parents[2] / "app" / "data" / "lessons"


def _new_tabu_state(lesson_id: str | None) -> TabuState | None:
    """Pick a secret word if the lesson is tabu. None for any other chat."""
    if not lesson_id:
        return None
    lesson = load_lesson(lesson_path=LESSONS_DIR / f"{lesson_id}.toml")
    if not lesson or not isinstance(lesson.lesson_instructions, TabuInstructions):
        return None
    card = random.choice(lesson.lesson_instructions.vocabulary)
    return TabuState(secret_word=card.word, forbidden_words=card.forbidden_words)


def _record_tabu_violations(chat_id: str, message: ChatMessage) -> None:
    """
    Save every forbidden word used in the learner's message.
    Same rule as useTabuGame: case-insensitive, word found anywhere in the text.
    Loads the chat inside the lock, so it always works on the newest file.
    """
    with chat_lock:
        state = get_chat(chat_id)
        if state is None or state.tabu is None:
            return

        text = message.content.lower()
        hits = [word for word in state.tabu.forbidden_words if word.lower() in text]
        if not hits:
            return

        now = now_local()
        for word in hits:
            state.tabu.violations.append(
                TabuViolation(word=word, message_id=message.id, created_at=now)
            )
        save_chat(state)


@router.post("/chat")
async def create_chat_endpoint(req: CreateChatRequest):
    """
    Create a new chat. Freezes everything that shapes the tutor (lesson, model,
    learner profile) into the chat's config, bound to whichever provider is active.
    The model saved here is the one every later call for this chat uses.
    For tabu lessons, the secret word is picked here and saved with the chat.
    """
    # Bind to whichever provider is currently active, and that provider's model.
    active = provider_state.active
    if active == "anthropic":
        bound_model = settings.anthropic_model
    else:
        bound_model = settings.default_model

    chat_id = f"chat-{uuid.uuid4()}"
    state = ChatState(
        chat_id=chat_id,
        config=ChatConfig(
            lesson_id=req.lesson_id,
            tutor_starts=req.tutor_starts,
            provider=active,
            model=bound_model,
            user=req.user_profile,
        ),
        tabu=_new_tabu_state(req.lesson_id),
        restarted_from=req.restarted_from,  # old chat_id when the learner pressed restart
    )
    # a brand-new file, so nothing to merge with. save_chat takes the lock itself.
    create_chat(state)
    return {
        "chat_id": chat_id,
        "tutor_starts": req.tutor_starts,
        "provider": active,
        "model": bound_model,
    }


@router.post("/chat/start")
def chat_start(req: StartChatRequest):
    """
    Tutor-starts flow. Call once after creating a chat when tutor_starts=True.
    Streams the tutor's opening message.
    """
    state = get_chat(req.chat_id)
    if not state:
        raise HTTPException(status_code=404, detail="Chat not found")
    if state.status == "terminated":
        raise HTTPException(
            status_code=410,
            detail={
                "code": "chat_terminated",
                "reason": state.terminated_reason,
                "message": "This conversation ended. Please start a new one.",
            },
        )

    return StreamingResponse(
        start_chat(chat_id=req.chat_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/chat/message")
def chat_message(req: ChatMessageRequest):
    """
    Send a message and stream the tutor's response.
    In tabu chats, violations are saved before streaming starts,
    so handle_message loads a chat that already contains them.
    """
    state = get_chat(req.chat_id)
    if not state:
        raise HTTPException(status_code=404, detail="Chat not found")
    if state.status == "terminated":
        raise HTTPException(
            status_code=410,
            detail={
                "code": "chat_terminated",
                "reason": state.terminated_reason,
                "message": "This conversation ended. Please start a new one.",
            },
        )

    if state.tabu is not None and req.message.role == "user" and not req.message.synthetic:
        _record_tabu_violations(req.chat_id, req.message)

    return StreamingResponse(
        handle_message(chat_id=req.chat_id, message=req.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/chat/{chat_id}/end")
def log_chat_end(chat_id: str, req: EndChatRequest):
    """
    Log how the chat ended (see ChatEndReason).
    The first reason wins, e.g. left_page after user_ended changes nothing.
    """
    with chat_lock:
        state = get_chat(chat_id)
        if not state:
            raise HTTPException(status_code=404, detail="Chat not found")

        if state.ended_reason is None:
            state.ended_reason = req.reason
            state.ended_at = now_local()
            save_chat(state)

        return {"ended_reason": state.ended_reason}


@router.post("/chat/{chat_id}/tabu/guessed")
def log_tabu_guessed(chat_id: str, req: TabuGuessRequest):
    """
    Log that the learner confirmed the tutor guessed the secret word.
    Only the first confirmation counts.
    """
    with chat_lock:
        state = get_chat(chat_id)
        if not state:
            raise HTTPException(status_code=404, detail="Chat not found")
        if state.tabu is None:
            raise HTTPException(status_code=400, detail="Not a tabu chat")

        if not state.tabu.guessed:
            state.tabu.guessed = True
            state.tabu.guessed_at = now_local()
            state.tabu.guess_source = req.source
            state.tabu.guessed_at_user_turn = sum(
                1 for m in state.messages if m.role == "user" and not m.synthetic
            )
            state.tabu.guessed_after_message_id = state.messages[-1].id if state.messages else None
            save_chat(state)

        return {"guessed": True, "guess_source": state.tabu.guess_source}


@router.delete("/chat/{chat_id}")
async def end_chat(chat_id: str):
    """End a chat. The saved JSON file stays on disk."""
    return {"ok": True}


@router.get("/chat/free/prompts")
async def get_free_chat_prompt(chat_id: str = Query(...)):
    """Return the system prompt for a free chat session, for display in the UI."""
    state = get_chat(chat_id)
    if not state:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat_model = ChatModel(
        config=state.config,
        chat_id=state.chat_id,
        lesson_config=None,
    )
    return {"chat_system_prompt": chat_model.system_prompt}