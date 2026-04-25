from fastapi import APIRouter, HTTPException, Query
from app.models.data.feedback import ImmediateFeedbackRequest, DetailedFeedbackRequest
from app.services.feedback import generate_immediate_feedback, generate_general_feedback
from app.services.session_store import get_session

router = APIRouter()

@router.post("/feedback/immediate")
async def get_immediate_feedback(req: ImmediateFeedbackRequest):
    result = generate_immediate_feedback(req.last_user_message, req.lesson_id, req.session_id)
    return result

@router.post("/feedback/detailed")
async def get_detailed_feedback(req: DetailedFeedbackRequest):
    result = generate_general_feedback(req.messages, req.lesson_id, req.session_id)
    return result