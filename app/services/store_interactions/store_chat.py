"""
JSON-file store for chats.

Layout (the chats dir is decided in set_storage: Python setter, env file, or default):
    <chats dir>/<date>/<username>_<browser_id>/<chat_id>.json             (this file)
    <chats dir>/<date>/<username>_<browser_id>/<chat_id>.feedback.json    (store_feedback)

The browser_id is a random id the frontend creates once per browser and keeps in
localStorage. Only its first 8 characters go in the folder name, so two participants
who pick the same username get separate folders. The full id is saved in the JSON.

The date is the day the chat was first saved, created when chat starts (create_chat),
overwritten throughout the conversation (peter's recommendation)

Each save sets timestamps on the state:
    created_at: set on the first save, never changed afterwards
    updated_at: refreshed on every save
The folder date is taken from created_at, so the two always agree.

It holds the full ChatState: messages, the chat's frozen config (lesson, model,
learner profile), timestamps, and any fields added to ChatState or ChatMessage later.
Merging chats with feedback happens during data analysis, not here.
On failure in saving, logs error.

Concurrency: any code that reads a chat, changes it and saves it again must hold
chat_lock for all three steps, so two requests can never overwrite each other.
One lock for all chats is enough, because each hold lasts milliseconds.
Requires a single uvicorn worker.
"""

import logging
import re
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from app.models.data.chat import ChatState
from .set_storage import get_chats_dir

logger = logging.getLogger(__name__)

TIMEZONE = ZoneInfo("Europe/Copenhagen")

BROWSER_ID_CHARS = 8  # how much of the browser id goes in the folder name

# one lock for every read-change-write on a chat file.
# RLock ("re-entrant"): the thread holding it may take it again, so code that
# holds it can still call save_chat, which takes it too.
chat_lock = threading.RLock()


# get values
def _safe(name: str) -> str:
    """
    make sure that names are safe for folders e.g., søren -> s_ren
    """
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def _user_folder(state: ChatState) -> str:
    """
    Folder name for one participant: username plus the start of their browser id,
    e.g. "anna_3f2a9c1e". Same name in two browsers -> two folders.
    """
    user = state.config.user
    short_id = _safe(user.browser_id)[:BROWSER_ID_CHARS]
    return f"{_safe(user.name)}_{short_id}"


def now_local() -> datetime:
    """Current time in Copenhagen, timezone-aware, to the second. Shared with store_feedback."""
    return datetime.now(TIMEZONE).replace(microsecond=0)


def _set_timestamps(state: ChatState) -> None:
    """
    Set created_at once (first save) and refresh updated_at on every save.
    Mutates the state so the in-memory copy keeps the same created_at.
    """
    now = now_local()
    if state.created_at is None:
        state.created_at = now
    state.updated_at = now


# pathing
def find_chat_path(chat_id: str) -> Path | None:
    """Locate an existing chat file when only the chat_id is known."""
    matches = list(get_chats_dir().glob(f"*/*/{_safe(chat_id)}.json"))
    return matches[0] if matches else None


def _path_for(state: ChatState) -> Path:
    """
    Reuse the existing file if there is one, so the date never changes.
    New chats go in the folder for the day of created_at.
    Call _set_timestamps(state) before this, so created_at is set.
    """
    existing = find_chat_path(state.chat_id)
    if existing is not None:
        return existing
    return (
        get_chats_dir()
        / state.created_at.date().isoformat()
        / _user_folder(state)
        / f"{_safe(state.chat_id)}.json"
    )


# saving and getting
def save_chat(state: ChatState) -> bool:
    """
    Write the full state to disk, replacing any previous version atomically.
    Holds chat_lock while writing, so a save never runs during another
    read-change-write. Returns True on success. On failure, logs the error
    and returns False.
    """
    tmp_path: Path | None = None
    with chat_lock:
        try:
            _set_timestamps(state)
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