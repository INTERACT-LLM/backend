"""
Lesson-specific config
"""
from pydantic import BaseModel, Field
from typing import Literal, Union

LESSON_TYPES = Literal["roleplay", "vocabulary_game"]

class LessonInstructions(BaseModel):
    lesson_type: LESSON_TYPES
    scenario: str
    vocabulary: list = Field(default_factory=list)
    cultural_contexts: list[str] = Field(default_factory=list)

class RoleplayInstructions(LessonInstructions):
    lesson_type: Literal["roleplay"] = "roleplay"
    vocabulary: list[str] = Field(default_factory=list)

class TwentyQuestionsInstructions(LessonInstructions):
    lesson_type: Literal["vocabulary_game"] = "vocabulary_game"
    max_questions: int = 20

class TabuWord(BaseModel):
    word: str
    forbidden_words: list[str]

class TabuInstructions(LessonInstructions):
    lesson_type: Literal["vocabulary_game"] = "vocabulary_game"
    vocabulary: list[TabuWord] = Field(default_factory=list)
    
class LessonFeedback(BaseModel):
    feedback_focus: Literal["grammar", "fluency", "communication"] | None = None

class LessonPresentation(BaseModel):
    ui_title: str
    ui_short_description: str
    ui_long_description: str
    ui_goals: list[str]

class Lesson(BaseModel):
    id: str
    min_turns: int
    lesson_presentation: LessonPresentation
    lesson_instructions: Union[TabuInstructions, TwentyQuestionsInstructions, RoleplayInstructions, LessonInstructions]
    lesson_feedback: LessonFeedback

    @property
    def lesson_type(self):
        return self.lesson_instructions.lesson_type