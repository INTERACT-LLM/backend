"""
JSON-file store for chats.

Layout:
    storage/chats/<date>/<username>/<chat_id>.json             (this file)
    storage/chats/<date>/<username>/<chat_id>.feedback.jsonl   (store_feedback)

The date is the day the chat was first saved, created when chat starts (create_chat),
overwritten throughout the conversation (peter's recommendation)

It holds the full ChatState: messages, snapshotted session config,
lesson_id, and any fields added to ChatState or ChatMessage later.
Merging chats with feedback happens during data analysis, not here.
On failure in saving, logs error.
"""
import logging
import re
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from app.models.data.chat import ChatState

logger = logging.getLogger(__name__)

# setup stuff (path + timezone)
CHATS_DIR = Path(__file__).parents[4] / "storage" / "chats"
CHATS_DIR.mkdir(parents=True, exist_ok=True)

TIMEZONE = ZoneInfo("Europe/Copenhagen")


# get values
def _safe(name: str) -> str:
    """
    make sure that names are safe for folders e.g., søren -> s_ren
    """
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def _username_of(state: ChatState) -> str:
    return state.snapshotted_config.user.name


def _today() -> str:
    return datetime.now(TIMEZONE).date().isoformat()


# pathing
def find_chat_path(chat_id: str) -> Path | None:
    """Locate an existing chat file when only the chat_id is known."""
    matches = list(CHATS_DIR.glob(f"*/*/{_safe(chat_id)}.json"))  
    return matches[0] if matches else None


def _path_for(state: ChatState) -> Path:
    """
    Reuse the existing file if there is one, so the date never changes.
    """
    existing = find_chat_path(state.chat_id)
    if existing is not None:
        return existing
    return (
        CHATS_DIR
        / _today()
        / _safe(_username_of(state))
        / f"{_safe(state.chat_id)}.json" 
    )


# saving and getting
def save_chat(state: ChatState) -> bool:
    """
    Write the full state to disk, replacing any previous version atomically.
    Returns True on success. On failure, logs the error and returns False.
    """
    tmp_path: Path | None = None
    try:
        path = _path_for(state)
        path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False
        ) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(state.model_dump_json(indent=2))

        tmp_path.replace(path)
        return True

    except Exception:
        logger.exception("Could not save chat %s", state.chat_id)
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
        return False


# kept so existing imports (chat_service, routers) keep working.
create_chat = save_chat


def get_chat(chat_id: str) -> ChatState | None:
    path = find_chat_path(chat_id)
    if path is None:
        return None
    return ChatState.model_validate_json(path.read_text(encoding="utf-8"))