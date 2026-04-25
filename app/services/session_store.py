from app.models.environments.session import SessionConfig

_store: dict[str, SessionConfig] = {}

def create_session(session_id: str, config: SessionConfig) -> None:
    _store[session_id] = config

def get_session(session_id: str) -> SessionConfig | None:
    return _store.get(session_id)

def delete_session(session_id: str) -> None:
    _store.pop(session_id, None)