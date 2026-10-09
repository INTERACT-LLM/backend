"""
JSONL store for immediate feedback.
Lives next to the chat file:
    storage/chats/<date>/<username>/<chat_id>.feedback.jsonl
One line per feedback event. Append-only, so it never races with save_chat.
On failure, logs failure !
"""
import logging  
from pathlib import Path

from app.models.data.feedback import FeedbackRecord
from .store_chat import find_chat_path

logger = logging.getLogger(__name__)  


def _feedback_path(chat_id: str) -> Path | None:
    """Same folder and name as the chat file, different extension."""
    chat_path = find_chat_path(chat_id)
    if chat_path is None:
        return None
    return chat_path.with_name(f"{chat_path.stem}.feedback.jsonl")


def save_feedback(record: FeedbackRecord) -> bool:
    """
    Append one record.
    Returns True on success. On failure, logs the error and returns False.
    """
    try:  
        path = _feedback_path(record.chat_id)
        if path is None:
            logger.warning("No chat file for %s, feedback not saved", record.chat_id)
            return False
        with path.open("a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")
        return True

    except Exception:  
        logger.exception("Could not save feedback for chat %s", record.chat_id)
        return False


def get_feedback(chat_id: str) -> list[FeedbackRecord]:
    """Read all feedback for a chat, in the order it was written."""
    path = _feedback_path(chat_id)
    if path is None or not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [
            FeedbackRecord.model_validate_json(line)
            for line in f
            if line.strip()
        ]