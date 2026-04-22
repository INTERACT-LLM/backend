"""
Add request and response handling here
"""

from fastapi import APIRouter
from app.models.data.chat import ChatRequest
from app.services.chat import handle_conversation

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    messages = handle_conversation(
        message=request.message,
        session_id=request.session_id,
        lesson_id=request.lesson_id
    )

    return {
        "messages": [m.model_dump() for m in messages]
    }