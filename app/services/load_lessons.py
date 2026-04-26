from pathlib import Path
import tomllib
from app.models.environments.lesson import (
    Lesson, LessonInstructions, RoleplayInstructions, TwentyQuestionsInstructions, TabuInstructions
)

def load_lesson(lesson_path: Path) -> Lesson:
    with open(lesson_path, "rb") as f:
        data = tomllib.load(f)

    instructions_data = data.get("lesson_instructions", {})
    lesson_type = instructions_data.get("lesson_type")
    vocabulary = instructions_data.get("vocabulary", [])

    # Pick the right instructions class based on structure of vocabulary
    if lesson_type == "roleplay":
        instructions = RoleplayInstructions.model_validate(instructions_data)
    elif lesson_type == "vocabulary_game":
        # Tabu has dicts with 'word' and 'forbidden_words', 20Q has plain strings
        if vocabulary and isinstance(vocabulary[0], dict):
            instructions = TabuInstructions.model_validate(instructions_data)
        else:
            instructions = TwentyQuestionsInstructions.model_validate(instructions_data)
    else:
        instructions = LessonInstructions.model_validate(instructions_data)

    data["lesson_instructions"] = instructions
    return Lesson.model_validate(data)
def load_all_lessons(lesson_dir) -> dict[str, Lesson]:
    if not lesson_dir.exists() or not lesson_dir.is_dir():
        raise ValueError(f"Directory {lesson_dir} does not exist or is not a directory.")

    lesson_paths = [p for p in lesson_dir.iterdir() if p.suffix == ".toml"]

    lessons = {}
    for path in lesson_paths:
        lessons[path.stem] = load_lesson(path)

    return lessons