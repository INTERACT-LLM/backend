"""
Add request and response handling here
"""

from fastapi import APIRouter

from app.models.chat import ChatMessage
from app.services.llm import generate_reply

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatMessage):
    generated_reply = generate_reply(request.content)

    return ChatMessage(content=generated_reply, role="assistant")
