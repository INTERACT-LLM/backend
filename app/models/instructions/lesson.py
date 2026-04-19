import tomllib

from pydantic import BaseModel, Field
from typing import Literal

LESSON_TYPES = Literal["roleplay", "vocabulary_game"]

class ModelInstructionsLesson(BaseModel):
    """
    Shape of data for task instructions sent to the Model
    """
    lesson_type: LESSON_TYPES
    scenario: str
    min_turns: int = 6
    vocabulary: list[str] = Field(default_factory=list)
    cultural_contexts: list[str] = Field(default_factory=list)
    feedback_focus: Literal["grammar", "fluency", "communication"] | None = None

class RoleplayInstructions(ModelInstructionsLesson):
    lesson_type: Literal["roleplay"] = "roleplay"

### game 
class TwentyQuestionsInstructions(ModelInstructionsLesson):
    lesson_type: Literal["vocabulary_game"] = "vocabulary_game"
    game_name: Literal["20_questions"] = "20_questions"
    max_questions: int = 20
    allow_hints: bool = True

# if I add more game types I could give Lesson a union like this 
# VocabularyGameInstructions = TwentyQuestionsInstructions | SomeOtherGameInstructions
# within Lesson model_instructions: RoleplayInstructions | VocabularyGameInstructions

class UserInstructionsLesson(BaseModel):
    """
    User / Student facing instructions
    """
    ui_title: str | None = None
    ui_short_description: str | None = None
    ui_long_description: str | None = None

class Lesson(BaseModel):
    """
    Defines a structured lesson that can be compiled into a system prompt.
    """
    id: str | None = None
    user_instructions: UserInstructionsLesson
    model_instructions: ModelInstructionsLesson

    @property
    def lesson_type(self):
        return self.model_instructions.lesson_type
    
if __name__ == "__main__":
    with open("data/lessons/game/20q_lesson.toml", "rb") as f:
        data = tomllib.load(f)

    lesson = Lesson.model_validate(data)