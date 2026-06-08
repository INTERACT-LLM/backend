"""
Data shapes for chats.
"""
from typing import Literal

from pydantic import BaseModel

from app.models.environments.session import SessionConfig


ProviderName = Literal["ollama", "vllm", "anthropic"]
ChatStatus = Literal["active", "terminated"]


class ChatMessage(BaseModel):
    role: str
    content: str
    synthetic: bool = False   # for the mixed_intiative user message that prompts the tutor to respond first


class ChatState(BaseModel):
    chat_id: str
    session_id: str
    lesson_id: str | None = None
    tutor_starts: bool = False
    snapshotted_config: SessionConfig
    messages: list[ChatMessage] = []

    # Provider binding: snapshotted at chat creation, immutable for the chat's lifetime.
    provider: ProviderName
    model: str

    # Lifecycle: chats are terminated (not deleted) when the provider becomes unreachable.
    status: ChatStatus = "active"
    terminated_reason: str | None = None


class CreateChatRequest(BaseModel):
    session_id: str
    lesson_id: str | None = None
    tutor_starts: bool = False
    model_id: str | None = None


class ChatMessageRequest(BaseModel):
    chat_id: str
    message: ChatMessage


class StartChatRequest(BaseModel):
    chat_id: str