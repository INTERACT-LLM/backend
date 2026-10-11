"""
Data shapes for chats.

ChatConfig is the key to how the chats are stored! Some variables below:

ChatEndReason
how the chat ended. The first reason that arrives is kept.
 - user_ended:          pressed "end lesson"
 - restarted:           pressed restart (this chat was replaced by a new one)
 - provider_terminated: the LLM provider became unreachable
 - left_page:           closed the tab, reloaded, or navigated away
 - None: still running, or the left_page signal never arrived

TabuGuessSource
- "nudge": answered yes to the "Did the tutor guess it?" popup
- "manual": pressed the "Tutor guessed it!" button themselves
"""
from datetime import datetime
import uuid
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.models.environments.user import UserProfile


ProviderName = Literal["ollama", "vllm", "anthropic"]
ChatStatus = Literal["active", "terminated"]

# variables to how the chat ended how the chat ended
ChatEndReason = Literal["user_ended", "restarted", "provider_terminated", "left_page"]
TabuGuessSource = Literal["nudge", "manual"]

# chat messages 
def _new_message_id() -> str:
    return f"msg-{uuid.uuid4()}"

class ChatMessage(BaseModel):
    id: str = Field(default_factory=_new_message_id)  # links a message to its feedback
    role: str
    content: str
    synthetic: bool = False   # for the mixed_intiative user message that prompts the tutor to respond first

# some taboo-related stuff that needs to be saved
class TabuViolation(BaseModel):
    word: str          # the forbidden word the learner used
    message_id: str    # links to ChatMessage.id
    created_at: datetime | None = None

class TabuState(BaseModel):
    secret_word: str
    forbidden_words: list[str]
    violations: list[TabuViolation] = Field(default_factory=list)

    # set when the learner confirms the tutor guessed the word
    guessed: bool = False
    guessed_at: datetime | None = None
    guess_source: TabuGuessSource | None = None
    guessed_at_user_turn: int | None = None        # learner turns so far when they pressed
    guessed_after_message_id: str | None = None    # last saved message when they pressed


# everythign that shaped the tutor's behaviour, frozen at chat creation.
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

    # how the chat ended (see ChatEndReason)
    ended_reason: ChatEndReason | None = None
    ended_at: datetime | None = None

    # chat_id of the chat this one replaced, when the learner pressed restart
    restarted_from: str | None = None

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
    restarted_from: str | None = None  # old chat_id when this chat comes from a restart


class ChatMessageRequest(BaseModel):
    chat_id: str
    message: ChatMessage


class StartChatRequest(BaseModel):
    chat_id: str


class EndChatRequest(BaseModel):
    reason: ChatEndReason


class TabuGuessRequest(BaseModel):
    source: TabuGuessSource