"""
Chat endpoints.
Handles chat lifecycle: creation, tutor opener, message turns, and cleanup.
"""
import uuid

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.models.data.chat import CreateChatRequest, ChatMessageRequest, StartChatRequest, ChatState
from app.models.llms.chat_model import ChatModel
from app.services.chat import start_chat, handle_message
from app.services.store_chat import create_chat, get_chat, delete_chat
from app.services.store_session import get_session

router = APIRouter()


@router.post("/chat")
async def create_chat_endpoint(req: CreateChatRequest):
    """
    Create a new chat and snapshot the current session config.
    Returns chat_id and tutor_starts so the frontend knows whether to call /chat/start.
    """
    session_config = get_session(req.session_id)
    if not session_config:
        raise HTTPException(status_code=404, detail="Session not found")

    chat_id = f"chat-{uuid.uuid4()}"
    state = ChatState(
        chat_id=chat_id,
        session_id=req.session_id,
        lesson_id=req.lesson_id,
        tutor_starts=req.tutor_starts,
        snapshotted_config=session_config,
    )
    create_chat(state)
    return {"chat_id": chat_id, "tutor_starts": req.tutor_starts}


@router.post("/chat/start")
def chat_start(req: StartChatRequest):
    """
    Tutor-starts flow. Call once after creating a chat when tutor_starts=True.
    Streams the tutor's opening message.
    """
    state = get_chat(req.chat_id)
    if not state:
        raise HTTPException(status_code=404, detail="Chat not found")

    return StreamingResponse(
        start_chat(chat_id=req.chat_id, model_id=req.model_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/chat/message")
def chat_message(req: ChatMessageRequest):
    """Send a message and stream the tutor's response."""
    state = get_chat(req.chat_id)
    if not state:
        raise HTTPException(status_code=404, detail="Chat not found")

    return StreamingResponse(
        handle_message(
            chat_id=req.chat_id,
            message=req.message,
            model_id=req.model_id,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.delete("/chat/{chat_id}")
async def end_chat(chat_id: str):
    """End a chat and clean up its history."""
    delete_chat(chat_id)
    return {"ok": True}


@router.get("/chat/free/prompts")
async def get_free_chat_prompt(chat_id: str = Query(...)):
    """Return the system prompt for a free chat session, for display in the UI."""
    state = get_chat(chat_id)
    if not state:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat_model = ChatModel(
        session_config=state.snapshotted_config,
        lesson_config=None,
    )
    return {"chat_system_prompt": chat_model.system_prompt}