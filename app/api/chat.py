"""
Add request and response handling here
"""
from app.services.llm import generate_reply
from fastapi import APIRouter
from app.models.chat import ChatMessage

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatMessage):
    generated_reply = generate_reply(request.message)

    return generated_reply

