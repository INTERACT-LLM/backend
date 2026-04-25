""" 
Session-specific config
"""

from pydantic import BaseModel
from typing import Literal


class UserProfile(BaseModel):  
    name: str = "Mina"
    language: str = "Spanish"
    proficiency_level: Literal["beginner", "intermediate", "advanced"]
    preferences: str | None = None

class SessionConfig(BaseModel):
    user: UserProfile

    @property
    def language(self) -> str:
        return self.user.language