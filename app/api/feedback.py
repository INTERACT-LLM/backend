import logging

from fastapi import APIRouter
from app.models.data.feedback import (
    ImmediateFeedbackRequest,
    DetailedFeedbackRequest,
    FeedbackRecord,
)
from app.services.feedback import generate_immediate_feedback, generate_general_feedback
from app.services.store_interactions.store_feedback import save_feedback

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/feedback/immediate")
async def get_immediate_feedback(req: ImmediateFeedbackRequest):
    result = generate_immediate_feedback(
        req.last_user_message,
        req.lesson_id,
        req.chat_id,
    )

    # Saving must never stop the feedback from reaching the learner.
    try:
        save_feedback(FeedbackRecord(
            chat_id=req.chat_id,
            message_id=req.message_id,
            user_message=req.last_user_message,
            status=result.get("feedback_status", "error"),
            feedback=result.get("FeedbackResponse"),
            detail=result.get("detail"),
        ))
    except Exception:
        logger.exception("Could not build feedback record for chat %s", req.chat_id)

    return result


@router.post("/feedback/detailed")
async def get_detailed_feedback(req: DetailedFeedbackRequest):
    return generate_general_feedback(
        req.messages,
        req.lesson_id,
        req.chat_id,
    )