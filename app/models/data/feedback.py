from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

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
    One line in <chat_id>.feedback.jsonl.
    Immediate records link to their message in <chat_id>.json through message_id.
    General records cover the whole chat, so they have no message_id.
    """
    kind: FeedbackKind = "immediate"         # lines saved before this field existed are immediate
    chat_id: str
    message_id: str | None = None            # immediate only
    user_message: dict | None = None         # immediate only, stored as sent by the frontend
    status: str                              # "success" or "error"
    feedback: FeedbackResponse | GeneralFeedbackResponse | None = None  # None when feedback failed
    detail: str | None = None                # error message, if any
    raw_output: str | None = None            # general only, the model's text, kept even if parsing failed
    model: str | None = None
    created_at: datetime | None = None