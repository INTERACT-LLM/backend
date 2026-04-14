"""
Format shape of data
"""

from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    message: str
    role: str = Literal["user", "assistant, system"]
