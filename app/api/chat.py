"""
Add request and response handling here
"""
from app.services.llm import generate_reply
from fastapi import APIRouter
from app.models.chat import ChatMessage

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatMessage):
    user_response = ChatMessage(message=request.message, role="user")

    generated_reply = generate_reply(request.message)

    model_response = ChatMessage(message=generated_reply, role="assistant")

    return model_response

