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


def _raw_if_failed(result: dict) -> str | None:
    """Keep the model's raw text only when parsing failed. On success, `feedback` holds it already."""
    if result.get("feedback_status") == "success":
        return None
    return result.get("raw_output")


# plain def, not async def: the LLM call blocks, and FastAPI runs a def endpoint
# in its own thread, so other learners' requests keep running meanwhile
@router.post("/feedback/immediate")
def get_immediate_feedback(req: ImmediateFeedbackRequest):
    result = generate_immediate_feedback(
        req.last_user_message,
        req.lesson_id,
        req.chat_id,
    )

    # Saving must never stop the feedback from reaching the learner.
    try:
        save_feedback(FeedbackRecord(
            kind="immediate",
            chat_id=req.chat_id,
            message_id=req.message_id,
            user_message=req.last_user_message,
            status=result.get("feedback_status", "error"),
            feedback=result.get("FeedbackResponse"),
            error=result.get("error"),
            raw_output=_raw_if_failed(result),
        ))
    except Exception:
        logger.exception("Could not build immediate feedback record for chat %s", req.chat_id)

    return result


@router.post("/feedback/detailed")
def get_detailed_feedback(req: DetailedFeedbackRequest):
    result = generate_general_feedback(
        req.messages,
        req.lesson_id,
        req.chat_id,
    )

    # Same rule: saving must never stop the feedback from reaching the learner.
    try:
        save_feedback(FeedbackRecord(
            kind="general",
            chat_id=req.chat_id,
            status=result.get("feedback_status", "error"),
            feedback=result.get("GeneralFeedbackResponse"),
            error=result.get("error"),
            raw_output=_raw_if_failed(result),
        ))
    except Exception:
        logger.exception("Could not build general feedback record for chat %s", req.chat_id)

    return result