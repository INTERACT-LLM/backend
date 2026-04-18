from app.models.instructions.lesson import Lesson
from app.models.instructions.general import GeneralModelInstructions

def build_general_instructions(general_instructions: GeneralModelInstructions, join_string: bool = False) -> list[str] | str:
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

def build_system_prompt(lesson: Lesson, general_instructions: GeneralModelInstructions) -> str:
    parts: list[str] = []

    if general_instructions:
        parts.extend(build_general_instructions(general_instructions, join_string=False))
    else: 
        raise ValueError("General instructions are required to build the system prompt.")

    # required sections
    if lesson.scenario:
        parts.append(f"This is the task scenario that you need to facilitate: {lesson.scenario}")
    else: 
        raise ValueError("Scenario is required in the lesson instructions to build the system prompt.")

    # lists
    if lesson.feedback_focus:
        parts.append(f"Focus: {lesson.feedback_focus}")

    if lesson.vocabulary_list:
        parts.append(f"Vocabulary: {', '.join(lesson.vocabulary_list)}")

    if lesson.cultural_contexts:
        parts.append(f"Cultural context: {'; '.join(lesson.cultural_contexts)}")

    return "\n\n".join(parts).strip() # avoid trailing newlines