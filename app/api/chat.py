"""
Add request and response handling here
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.data.chat import ChatRequest
from app.services.chat import handle_conversation

router = APIRouter()

@router.post("/chat")
def chat(request: ChatRequest):
    return StreamingResponse(
        handle_conversation(
            message=request.message,
            session_id=request.session_id,
            lesson_id=request.lesson_id,
            model_id=request.model_id,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )