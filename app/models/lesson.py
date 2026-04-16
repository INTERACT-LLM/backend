from pydantic import BaseModel
from typing import Literal

class Lesson(BaseModel):
    """
    Defines a structured lesson that can be compiled into a system prompt.
    """
    id: str | None = None
    ui_title: str | None = None
    ui_lesson_description: str | None = None

    initial_system_prompt: str
    scenario: str
    min_turns: int = 5

    vocabulary_list: list[str] = []
    cultural_contexts: list[str] = [] 

    student_level: Literal["beginner", "intermediate", "advanced"] | None = None

    feedback_focus: Literal["grammar", "fluency", "communication"] | None = None

def build_system_prompt(lesson: Lesson) -> str:
    parts: list[str] = []

    # base instruction
    parts.append(lesson.initial_system_prompt)

    # required sections
    parts.append(f"Scenario: {lesson.scenario}")

    # optional sections
    if lesson.student_level:
        parts.append(f"Student level: {lesson.student_level}")

    if lesson.feedback_focus:
        parts.append(f"Focus: {lesson.feedback_focus}")

    # lists
    if lesson.vocabulary_list:
        parts.append(f"Vocabulary: {', '.join(lesson.vocabulary_list)}")

    if lesson.cultural_contexts:
        parts.append(f"Cultural context: {'; '.join(lesson.cultural_contexts)}")

    return "\n\n".join(parts).strip() # avoid trailing newlines