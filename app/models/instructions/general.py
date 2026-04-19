from pydantic import BaseModel
from typing import Literal

class ModelInstructionsGeneral(BaseModel):
    """
    General instructions for the Model, not specific to a lesson.
    """
    language_to_teach: Literal["Spanish", "French", "German"]
    system_prompt: str
    user_level: Literal["beginner", "intermediate", "advanced"] | None = None
    user_preferences: str | None = None