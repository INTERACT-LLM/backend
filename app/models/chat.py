"""
Format shape of data
"""

from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    content: str
    role: Literal["user", "assistant", "system"] = "user"

class ChatRequest(BaseModel):
    """
    Model 

    Attributes: 
        messages: list of messages in conversation
        conversation_id: unique identifier for the conversation 
        lesson_id: unique identifier for the lesson (to select lesson-specific system prompts)

    NB. consider adding session_id or user_id in the future for more personalized conversations and analytics
    """
    messages: list[ChatMessage]
    conversation_id: str | None = None
    lesson_id: str | None = None
