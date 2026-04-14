"""
Add request and response handling here
"""
from fastapi import APIRouter
from app.models.chat import ChatRequest

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    response = {
        "message": f"Received message: {request.message}",
        "conversation_id": request.conversation_id or "new_conversation_id"
    }
    return response

