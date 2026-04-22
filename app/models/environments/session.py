""" 
Session-specific config
"""

from pydantic import BaseModel
from typing import Literal


class UserData(BaseModel):  
    name: str = "Mina"
    proficiency_level: Literal["beginner", "intermediate", "advanced"]
    preferences: str | None = None

class SessionConfig(BaseModel):
    """
    Session-specifc toml that will be used both for building chatmodel system prompt + feedback model
    """
    language: Literal["spanish", "french", "german"]
    user: UserData