from pydantic import BaseModel
from typing import Literal

class ModelInstructionsLesson(BaseModel):
    """
    Shape of data for task instructions sent to the Model
    """
    scenario: str
    min_turns: int = 6

    vocabulary_list: list[str] = []
    cultural_contexts: list[str] = [] 
    
    feedback_focus: Literal["grammar", "fluency", "communication"] | None = None

class UserInstructionsLesson(BaseModel):
    """
    User / Student facing instructions
    """
    ui_title: str | None = None
    ui_lesson_description: str | None = None
    ui_long_lesson_description: str | None = None

class Lesson(BaseModel):
    """
    Defines a structured lesson that can be compiled into a system prompt.
    """
    id: str | None = None
    user_instructions: UserInstructionsLesson
    model_instructions: ModelInstructionsLesson