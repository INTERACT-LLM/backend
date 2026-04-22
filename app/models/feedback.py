"""
Define structure of feedback to generate structured JSON feedback from feedback model 
(see also app/services/feedback.py for feedback generation logic)
"""
from pydantic import BaseModel

# structured feedback response model (for ollama structured output)
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