from pydantic import BaseModel

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

class DetailedFeedbackRequest(BaseModel):
    messages: list[dict]
    lesson_id: str | None = None
    chat_id: str