from fastapi import APIRouter
from app.models.feedback import ImmediateFeedbackRequest, DetailedFeedbackRequest
from app.services.feedback import generate_immediate_feedback, generate_general_feedback

router = APIRouter()

@router.post("/feedback/immediate")
async def get_immediate_feedback(feedback_request: ImmediateFeedbackRequest):
    result = generate_immediate_feedback(feedback_request.last_user_message)
    return result

@router.post("/feedback/detailed")
async def get_detailed_feedback(feedback_request: DetailedFeedbackRequest):
    result = generate_general_feedback(feedback_request.messages)
    return result