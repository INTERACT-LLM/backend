"""
Define structure of feedback to generate structured JSON feedback from feedback model 
(see also app/services/feedback.py for feedback generation logic)
"""
from pydantic import BaseModel

class FeedbackResponse(BaseModel):
    session_id: str
    has_error: bool
    corrected_text: str | None
    explanation: str | None