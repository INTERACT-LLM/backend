"""
Format shape of data
"""
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: ChatMessage
    lesson_id: str | None = None
    session_id: str