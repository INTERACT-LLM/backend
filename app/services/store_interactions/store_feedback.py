"""
JSON store for feedback, both immediate (per message) and general (end of chat).
Lives next to the chat file:
    storage/chats/<date>/<username>_<browser_id>/<chat_id>.feedback.json
The file holds one list of records, oldest first, each marked by kind
("immediate" or "general").

Adding a record reads the list, appends, and writes the whole file back,
replacing it atomically (same approach as store_chat), so a crash never
leaves a half-written file. A lock makes sure only one save runs at a time,
so two saves can never overwrite each other. Saves take milliseconds, so
one lock for all chats is enough. Requires a single uvicorn worker.

Each record gets a created_at timestamp (Copenhagen time) unless the caller set one.
No updated_at: a record is written once and never changed.
On failure, logs failure !
"""
import logging
import tempfile
import threading
from pathlib import Path

from pydantic import TypeAdapter

from app.models.data.feedback import FeedbackRecord
from .store_chat import find_chat_path, now_local

logger = logging.getLogger(__name__)

# reads and writes a whole list of FeedbackRecord in one go
_RECORDS = TypeAdapter(list[FeedbackRecord])

# only one save at a time, so a second save always reads the first one's result
_SAVE_LOCK = threading.Lock()


def _feedback_path(chat_id: str) -> Path | None:
    """Same folder and name as the chat file, different extension."""
    chat_path = find_chat_path(chat_id)
    if chat_path is None:
        return None
    return chat_path.with_name(f"{chat_path.stem}.feedback.json")


def get_feedback(chat_id: str) -> list[FeedbackRecord]:
    """Read all feedback for a chat, in the order it was written."""
    path = _feedback_path(chat_id)
    if path is None or not path.exists():
        return []
    return _RECORDS.validate_json(path.read_bytes())


def save_feedback(record: FeedbackRecord) -> bool:
    """
    Add one record to the chat's feedback file, with a created_at timestamp.
    Returns True on success. On failure, logs the error and returns False.
    """
    tmp_path: Path | None = None
    try:
        path = _feedback_path(record.chat_id)
        if path is None:
            logger.warning("No chat file for %s, feedback not saved", record.chat_id)
            return False

        # set the timestamp only once we know the record will be written
        if record.created_at is None:
            record.created_at = now_local()

        # read, append and write as one step, so no other save can slip in between
        with _SAVE_LOCK:
            records = get_feedback(record.chat_id)
            records.append(record)

            with tempfile.NamedTemporaryFile(
                "wb", dir=path.parent, suffix=".tmp", delete=False
            ) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(_RECORDS.dump_json(records, indent=2))

            tmp_path.replace(path)
        return True

    except Exception:
        logger.exception("Could not save feedback for chat %s", record.chat_id)
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
        return False