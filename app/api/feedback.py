from fastapi import APIRouter
from app.models.data.feedback import ImmediateFeedbackRequest, DetailedFeedbackRequest
from app.services.feedback import generate_immediate_feedback, generate_general_feedback

router = APIRouter()

@router.post("/feedback/immediate")
async def get_immediate_feedback(req: ImmediateFeedbackRequest):
    return generate_immediate_feedback(
        req.last_user_message,
        req.lesson_id,
        req.session_id,
        model_id=req.model_id,
    )

@router.post("/feedback/detailed")
async def get_detailed_feedback(req: DetailedFeedbackRequest):
    return generate_general_feedback(
        req.messages,
        req.lesson_id,
        req.session_id,
        model_id=req.model_id,
    )