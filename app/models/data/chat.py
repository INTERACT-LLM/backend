"""
Data shapes for chats.
"""
from pydantic import BaseModel
from app.models.environments.session import SessionConfig


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatState(BaseModel):
    chat_id: str
    session_id: str
    lesson_id: str | None = None
    tutor_starts: bool = False
    snapshotted_config: SessionConfig
    messages: list[ChatMessage] = []


class CreateChatRequest(BaseModel):
    session_id: str
    lesson_id: str | None = None
    tutor_starts: bool = False


class ChatMessageRequest(BaseModel):
    chat_id: str
    message: ChatMessage
    model_id: str | None = None


class StartChatRequest(BaseModel):
    chat_id: str
    model_id: str | None = None