from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

TIMEZONE = ZoneInfo("Europe/Copenhagen")


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
    Linked to its message in <chat_id>.json through message_id.
    """
    chat_id: str
    message_id: str
    user_message: dict                       # stored as sent by the frontend
    status: str                              # "success" or "error"
    feedback: FeedbackResponse | None = None # None when feedback failed
    detail: str | None = None                # error message, if any
    model: str | None = None
    created_at: datetime | None = None