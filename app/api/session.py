"""
Session lifecycle endpoints.
Manages user identity and profile for the duration of a visit.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.environments.session import SessionConfig, UserProfile
from app.services.store_session import create_session, get_session, update_session, delete_session

router = APIRouter()


class SessionInitRequest(BaseModel):
    session_id: str
    user_profile: UserProfile


@router.post("/session")
async def init_session(req: SessionInitRequest):
    """Create a new user session with profile info."""
    config = SessionConfig(session_id=req.session_id, user=req.user_profile)
    create_session(req.session_id, config)
    return {"ok": True}


@router.patch("/session/{session_id}")
async def update_session_profile(session_id: str, user_profile: UserProfile):
    """
    Update user profile fields (e.g. language, proficiency).
    Only affects new chats — in-progress chats use their snapshotted config.
    """
    updated = update_session(session_id, user_profile)
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True, "updated": updated}


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """End the user session. Chat cleanup is handled separately via DELETE /chat/{chat_id}."""
    delete_session(session_id)
    return {"ok": True}