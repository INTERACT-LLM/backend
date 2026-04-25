from fastapi import APIRouter
from pydantic import BaseModel
from app.models.environments.session import SessionConfig, UserProfile
from app.services.session_store import create_session, delete_session, get_session, _store

router = APIRouter()

class SessionInitRequest(BaseModel):
    session_id: str
    user_profile: UserProfile

@router.post("/session")
async def init_session(req: SessionInitRequest):
    print(f"init_session called with session_id: {req.session_id}")
    print(f"user_profile: {req.user_profile}")
    config = SessionConfig(user=req.user_profile)
    create_session(req.session_id, config)
    print(f"store after save: {list(_store.keys())}")
    return {"ok": True}

@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    delete_session(session_id)
    return {"ok": True}