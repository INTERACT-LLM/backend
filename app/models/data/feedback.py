from pydantic import BaseModel

class FeedbackResponse(BaseModel):
    has_language_error: bool
    corrected_text: str | None
    english_error_explanation: str | None

class GeneralFeedbackResponse(BaseModel):
    positive: list[str]
    improvements: list[str]

# for api request bodies
class ImmediateFeedbackRequest(BaseModel):
    last_user_message: dict

class DetailedFeedbackRequest(BaseModel):
    messages: list[dict]
