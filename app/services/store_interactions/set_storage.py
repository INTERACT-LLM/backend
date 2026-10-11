"""
Where chats and their feedback are saved. Decided in this order:
  1. set_chats_dir(path) in Python, e.g. in a test or analysis script
  2. CHATS_DIR in the env file (APP_ENV) or the shell
  3. default: <project root>/storage/chats
Relative paths always start at the project root.
"""
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parents[4]
DEFAULT_CHATS_DIR = PROJECT_ROOT / "storage" / "chats"


class StorageSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("APP_ENV"),
        env_file_encoding="utf-8",
        extra="ignore",  # the env file also holds LLM settings; skip them here
    )
    chats_dir: Path = DEFAULT_CHATS_DIR


def _resolve(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


_chats_dir = _resolve(StorageSettings().chats_dir)
_chats_dir.mkdir(parents=True, exist_ok=True)


def get_chats_dir() -> Path:
    return _chats_dir


def set_chats_dir(path: str | Path) -> Path:
    """Use another folder from now on, in this Python process only."""
    global _chats_dir
    _chats_dir = _resolve(path)
    _chats_dir.mkdir(parents=True, exist_ok=True)
    return _chats_dir