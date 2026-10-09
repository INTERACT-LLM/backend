"""
In-memory store for user sessions.
Holds user identity and profile config for the duration of a visit.
"""
from app.models.environments.session import SessionConfig, UserProfile

_sessions: dict[str, SessionConfig] = {}


def create_session(session_id: str, config: SessionConfig) -> None:
    _sessions[session_id] = config


def get_session(session_id: str) -> SessionConfig | None:
    return _sessions.get(session_id)


def update_session(session_id: str, updates: UserProfile) -> SessionConfig | None:
    """Update user profile fields. Only overwrites provided fields."""
    config = _sessions.get(session_id)
    if not config:
        return None
    updated = config.model_copy(update={"user": updates})
    _sessions[session_id] = updated
    return updated


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)