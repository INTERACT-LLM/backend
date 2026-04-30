"""
Add request and response handling here
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.models.data.chat import ChatRequest
from app.models.llms.chat_model import ChatModel
from app.services.chat import handle_conversation
from app.services.session_store import get_session

router = APIRouter()

@router.post("/chat")
def chat(request: ChatRequest):
    return StreamingResponse(
        handle_conversation(
            message=request.message,
            session_id=request.session_id,
            lesson_id=request.lesson_id,
            model_id=request.model_id,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@router.get("/chat/free/prompts")
async def get_free_chat_prompt(session_id: str = Query(...)):
    if session_id == "undefined" or not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    session_config = get_session(session_id)
    if not session_config:
        raise HTTPException(status_code=404, detail="Session not found")

    chat_model = ChatModel(
        session_config=session_config,
        lesson_config=None,
    )

    return {"chat_system_prompt": chat_model.system_prompt}