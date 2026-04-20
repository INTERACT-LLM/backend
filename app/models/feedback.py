"""
Define structure of feedback to generate structured JSON feedback from feedback model 
(see also app/services/feedback.py for feedback generation logic)
"""
from pydantic import BaseModel

class FeedbackResponse(BaseModel):
    has_error: bool
    corrected_text: str | None
    english_error_explanation: str | None

class FeedbackRequest(BaseModel):
    last_user_message: dict
