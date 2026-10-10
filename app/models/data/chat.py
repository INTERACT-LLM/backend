"""
Data shapes for chats.
"""
from datetime import datetime
import uuid
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.models.environments.user import UserProfile  


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


# everything that shaped the tutor's behaviour, frozen at chat creation.
# Everything that shaped the tutor's behaviour, frozen at chat creation.
class ChatConfig(BaseModel):
    # Label for data analysis only, the app logic keeps using lesson_id.
    # I use lesson_id being None to skip loading lessons, so it stays as it is.
    # Empty placeholder here, always filled in from lesson_id by _set_chat_type.
    chat_type: Literal["lesson", "free_chat"] | None = None

    lesson_id: str | None = None
    tutor_starts: bool = False

    # provider binding: immutable for the chat's lifetime.
    provider: ProviderName
    model: str

    user: UserProfile

    @property
    def language(self) -> str:
        return self.user.language

    @model_validator(mode="after")
    def _set_chat_type(self):
        """'lesson' when the chat has a lesson_id, otherwise 'free_chat'."""
        self.chat_type = "lesson" if self.lesson_id else "free_chat"
        return self


class ChatState(BaseModel):
    # identity and lifecycle
    chat_id: str
    
    # chats are terminated (not deleted) when the provider becomes unreachable.
    status: ChatStatus = "active"
    terminated_reason: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # lesson_id, tutor_starts, provider, model
    config: ChatConfig

    # game state
    tabu: TabuState | None = None

    messages: list[ChatMessage] = []


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