"""
Chat endpoints.
Handles chat lifecycle: creation, tutor opener, message turns, and cleanup.
"""
import random
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.models.data.chat import (
    CreateChatRequest, ChatMessageRequest, StartChatRequest,
    ChatState, ChatConfig, ChatMessage, TabuState, TabuViolation,  
)
from app.models.environments.lesson import TabuInstructions
from app.models.llms.chat_model import ChatModel
from app.services.chat import start_chat, handle_message
from app.services.load_lessons import load_lesson
from app.services.model_config import settings
from app.services.provider_state import provider_state # for fallback logic
from app.services.store_interactions.store_chat import create_chat, get_chat, save_chat, now_local

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


def _record_tabu_violations(state: ChatState, message: ChatMessage) -> None:
    """
    Save every forbidden word used in the learner's message.
    Same rule as useTabuGame: case-insensitive, word found anywhere in the text.
    """
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
    For tabu lessons, the secret word is picked here and saved with the chat.
    """
    # Bind to whichever provider is currently active.
    active = provider_state.active
    if active == "anthropic":
        bound_model = settings.anthropic_model
    else:
        bound_model = req.model_id or settings.default_model

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
    )
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
        _record_tabu_violations(state, req.message)

    return StreamingResponse(
        handle_message(chat_id=req.chat_id, message=req.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


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