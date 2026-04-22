"""
Lesson-specific config
"""
from pydantic import BaseModel, Field
from typing import Literal

LESSON_TYPES = Literal["roleplay", "vocabulary_game"]

class LessonInstructions(BaseModel):
    """
    Instructions for the chat model, specific to the lesson.
    """
    lesson_type: LESSON_TYPES
    scenario: str
    vocabulary: list[str] = Field(default_factory=list)
    cultural_contexts: list[str] = Field(default_factory=list)

class RoleplayInstructions(LessonInstructions):
    lesson_type: Literal["roleplay"] = "roleplay"

class TwentyQuestionsInstructions(LessonInstructions):
    lesson_type: Literal["vocabulary_game"] = "vocabulary_game"
    game_name: Literal["20_questions"] = "20_questions"
    max_questions: int = 20 

class LessonFeedback(BaseModel):
    """
    Instructions for the feedback model, specific to the lesson.
    """
    feedback_focus: Literal["grammar", "fluency", "communication"] | None = None

class LessonPresentation(BaseModel):
    """
    How the lesson is presented. This is seperate from instructions to the model.
    """
    ui_title: str 
    ui_short_description: str 
    ui_long_description: str

class Lesson(BaseModel):
    """
    Defines a structured lesson that can be compiled into a system prompt.
    """
    id: str 
    min_turns: int
    lesson_presentation: LessonPresentation
    lesson_instructions: LessonInstructions
    lesson_feedback: LessonFeedback


    @property
    def lesson_type(self):
        return self.lesson_instructions.lesson_type