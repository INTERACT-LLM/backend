import random

from app.models.instructions.lesson import Lesson, ModelInstructionsLesson, RoleplayInstructions, TwentyQuestionsInstructions
from app.models.instructions.general import ModelInstructionsGeneral

def build_general_instructions(general_instructions: ModelInstructionsGeneral, join_string: bool = False) -> list[str] | str:
    parts: list[str] = []

    if general_instructions.system_prompt:
        parts.append(general_instructions.system_prompt)

    if general_instructions.user_level:
        parts.append(f"Student level is: {general_instructions.user_level}")

    if general_instructions.user_preferences:
        parts.append(f"Here is some information about the student's preferences: {general_instructions.user_preferences}")

    if join_string:
        return "\n\n".join(parts).strip() # avoid trailing newlines

    return parts

def add_vocabulary_to_prompt(parts, instructions: ModelInstructionsLesson) -> None:
    match instructions:
        case TwentyQuestionsInstructions():
            word = random.choice(instructions.vocabulary)
            parts.append(
                f"Secret word: {word}. Guide the student to guess it in "
                f"up to {instructions.max_questions} questions."
            )
        case RoleplayInstructions():
            parts.append(f"Incorporate these words naturally: {', '.join(instructions.vocabulary)}")

    return parts

def build_system_prompt(lesson: Lesson, general_instructions: ModelInstructionsGeneral) -> str:
    parts: list[str] = []

    ## GENERAL INSTRUCTIONS ##
    if not general_instructions:
        raise ValueError("General instructions are required to build the system prompt.")

    parts = build_general_instructions(general_instructions, join_string=False)
    
    ## LESSON-SPECIFIC INSTRUCTIONS ##
    mi = lesson.model_instructions

    parts.append(f"The lesson type is: {lesson.lesson_type}")
    
    if not mi.scenario:
        raise ValueError("Scenario is required in the lesson instructions to build the system prompt.")

    parts.append(f"This is the task scenario that you need to facilitate: {mi.scenario}")

    if mi.feedback_focus:
        parts.append(f"Focus: {mi.feedback_focus}")

    if mi.vocabulary:
        parts = add_vocabulary_to_prompt(parts, mi)

    if mi.cultural_contexts:
        parts.append(f"Cultural context: {'; '.join(mi.cultural_contexts)}")

    return "\n\n".join(parts).strip()