"""
In-memory store for active chats.
Holds message history and snapshotted session config for each chat.
A new chat is created each time a user starts a lesson or free chat session.
"""
from app.models.data.chat import ChatState

_chats: dict[str, ChatState] = {}


def create_chat(state: ChatState) -> None:
    _chats[state.chat_id] = state


def get_chat(chat_id: str) -> ChatState | None:
    return _chats.get(chat_id)


def delete_chat(chat_id: str) -> None:
    _chats.pop(chat_id, None)