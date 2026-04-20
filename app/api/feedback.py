from fastapi import APIRouter
from app.services.feedback import generate_immediate_feedback

router = APIRouter()

@router.post("/feedback/{session_id}")
async def get_feedback(last_user_message: dict):
    result = generate_immediate_feedback(last_user_message)
    return result