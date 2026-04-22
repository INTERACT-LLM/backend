from fastapi import APIRouter, HTTPException, Query
from app.models.data.feedback import ImmediateFeedbackRequest, DetailedFeedbackRequest
from app.services.feedback import generate_immediate_feedback, generate_general_feedback

router = APIRouter()

@router.post("/feedback/immediate")
async def get_immediate_feedback(feedback_request: ImmediateFeedbackRequest, lesson_id: str | None = None):
    resolved_lesson_id = lesson_id or feedback_request.lesson_id
    if not resolved_lesson_id:
        raise HTTPException(status_code=400, detail="Missing lesson_id. Provide it in query params or request body.")

    result = generate_immediate_feedback(feedback_request.last_user_message, resolved_lesson_id)
    return result

@router.post("/feedback/detailed")
async def get_detailed_feedback(feedback_request: DetailedFeedbackRequest, lesson_id: str | None = None):
    resolved_lesson_id = lesson_id or feedback_request.lesson_id
    if not resolved_lesson_id:
        raise HTTPException(status_code=400, detail="Missing lesson_id. Provide it in query params or request body.")

    result = generate_general_feedback(feedback_request.messages, resolved_lesson_id)
    return result