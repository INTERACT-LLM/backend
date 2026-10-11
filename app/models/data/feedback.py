from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import AliasChoices, BaseModel, Field

TIMEZONE = ZoneInfo("Europe/Copenhagen")

# "immediate": feedback on one learner message, during the chat
# "general":   feedback on the whole chat, after "end lesson"
FeedbackKind = Literal["immediate", "general"]


class FeedbackResponse(BaseModel):
    has_language_error: bool
    corrected_text: str | None
    english_error_explanation: str | None


class GeneralFeedbackResponse(BaseModel):
    positive: list[str]
    improvements: list[str]


class ImmediateFeedbackRequest(BaseModel):
    last_user_message: dict
    lesson_id: str | None = None
    chat_id: str
    message_id: str                          # same id as the ChatMessage it belongs to


class DetailedFeedbackRequest(BaseModel):
    messages: list[dict]
    lesson_id: str | None = None
    chat_id: str


class FeedbackRecord(BaseModel):
    """
    One entry in the list in <chat_id>.feedback.json.
    Immediate records link to their message in <chat_id>.json through message_id.
    General records cover the whole chat, so they have no message_id.
    Every record has all fields; empty ones are saved as null.
    The model used is not stored here: it is always the chat's config.model.
    """
    kind: FeedbackKind = "immediate"         # records saved before this field existed are immediate
    chat_id: str
    message_id: str | None = None            # immediate only
    user_message: dict | None = None         # immediate only, stored as sent by the frontend
    status: str                              # "success" or "error"
    feedback: FeedbackResponse | GeneralFeedbackResponse | None = None  # null when feedback failed

    # why feedback failed. Older records called this "detail", so both names are read.
    error: str | None = Field(default=None, validation_alias=AliasChoices("error", "detail"))

    raw_output: str | None = None            # the model's text, only when parsing it failed
    created_at: datetime | None = None