import random

from app.models.instructions.lesson import Lesson, ModelInstructionsLesson, RoleplayInstructions, TwentyQuestionsInstructions
from app.models.instructions.general import ModelInstructionsGeneral

def build_general_instructions(general_instructions: ModelInstructionsGeneral) -> list[str]:
    parts = [
        general_instructions.system_prompt,
        f"You are teaching the language: {general_instructions.language_to_teach}",
    ]

    if general_instructions.user_level:
        parts.append(f"Student level is: {general_instructions.user_level}")

    if general_instructions.user_preferences:
        parts.append(f"Here is some information about the student's preferences: {general_instructions.user_preferences}")

    return parts

def add_vocabulary_to_prompt(parts: list[str], instructions: ModelInstructionsLesson) -> None:
    match instructions:
        case TwentyQuestionsInstructions():
            word = random.choice(instructions.vocabulary)
            parts.append(
                f"Secret word: {word}. Guide the student to guess it in "
                f"up to {instructions.max_questions} questions."
            )
        case RoleplayInstructions():
            parts.append(f"Incorporate these words naturally: {', '.join(instructions.vocabulary)}")

def build_system_prompt(lesson: Lesson, general_instructions: ModelInstructionsGeneral) -> str:
    parts: list[str] = []

    ## GENERAL INSTRUCTIONS ##
    parts = build_general_instructions(general_instructions)
    
    ## LESSON-SPECIFIC INSTRUCTIONS ##
    mi = lesson.model_instructions

    parts.append(f"The lesson type is: {lesson.lesson_type}")
    parts.append(f"This is the task scenario that you need to facilitate: {mi.scenario}")

    if mi.feedback_focus:
        parts.append(f"Focus: {mi.feedback_focus}")

    if mi.vocabulary:
        add_vocabulary_to_prompt(parts, mi)

    if mi.cultural_contexts:
        parts.append(f"Cultural context: {'; '.join(mi.cultural_contexts)}")

    return "\n\n".join(parts).strip()