"""
Data shapes for chats.
"""
from datetime import datetime
import uuid
from typing import Literal

from pydantic import BaseModel, Field

from app.models.environments.session import SessionConfig, UserProfile  


ProviderName = Literal["ollama", "vllm", "anthropic"]
ChatStatus = Literal["active", "terminated"]


def _new_message_id() -> str:
    return f"msg-{uuid.uuid4()}"


class ChatMessage(BaseModel):
    id: str = Field(default_factory=_new_message_id)  # links a message to its feedback
    role: str
    content: str
    synthetic: bool = False   # for the mixed_intiative user message that prompts the tutor to respond first

class TabuViolation(BaseModel):
    word: str          # the forbidden word the learner used
    message_id: str    # links to ChatMessage.id
    created_at: datetime | None = None

class TabuState(BaseModel):
    secret_word: str
    forbidden_words: list[str]
    violations: list[TabuViolation] = Field(default_factory=list)

class ChatState(BaseModel):
    chat_id: str
    lesson_id: str | None = None
    tutor_starts: bool = False
    snapshotted_config: SessionConfig
    messages: list[ChatMessage] = []

    # for tabu
    tabu: TabuState | None = None

    # Provider binding: snapshotted at chat creation, immutable for the chat's lifetime.
    provider: ProviderName
    model: str

    # Lifecycle: chats are terminated (not deleted) when the provider becomes unreachable.
    status: ChatStatus = "active"
    terminated_reason: str | None = None

    # dates
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CreateChatRequest(BaseModel):
    lesson_id: str | None = None
    tutor_starts: bool = False
    model_id: str | None = None
    user_profile: UserProfile


class ChatMessageRequest(BaseModel):
    chat_id: str
    message: ChatMessage


class StartChatRequest(BaseModel):
    chat_id: str