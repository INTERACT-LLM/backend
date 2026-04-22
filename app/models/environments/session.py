""" 
Session-specific config
"""

from pydantic import BaseModel
from typing import Literal


class UserData(BaseModel):  
    user_name: str = "Mina"
    user_level: Literal["beginner", "intermediate", "advanced"]
    user_preferences: str | None = None

class SessionConfig(BaseModel):
    """
    Session-specifc toml that will be used both for building chatmodel system prompt + feedback model
    """
    language: Literal["spanish", "french", "german"]
    user: UserData