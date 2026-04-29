"""
Format shape of data
"""
from pydantic import BaseModel
 
class ChatMessage(BaseModel):
    role: str
    content: str
 
class ChatRequest(BaseModel):
    message: ChatMessage
    session_id: str
    lesson_id: str
    model_id: str | None = None