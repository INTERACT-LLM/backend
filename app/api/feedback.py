from fastapi import APIRouter
from app.models.feedback import FeedbackRequest
from app.services.feedback import generate_immediate_feedback

router = APIRouter()

@router.post("/feedback/immediate")
async def get_feedback(feedback_request: FeedbackRequest):
    result = generate_immediate_feedback(feedback_request.last_user_message)
    return result