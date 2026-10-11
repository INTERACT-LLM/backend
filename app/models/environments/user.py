"""
Learner profile!
"""

from pydantic import BaseModel, Field
from typing import Literal


class UserProfile(BaseModel):
    name: str
    language: str = "Spanish"
    proficiency_level: Literal["beginner", "intermediate", "advanced"]
    preferences: str | None = None
    browser_id: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9-]+$")