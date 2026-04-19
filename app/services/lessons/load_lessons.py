from pathlib import Path 
import tomllib
from app.models.instructions.lesson import Lesson

def load_lesson(lesson_path: Path) -> Lesson:
    with open(lesson_path, "rb") as f:
        data = tomllib.load(f)  
    
    lesson = Lesson.model_validate(data)
    
    return lesson

def load_all_lessons(roleplay_dir: Path, vocabulary_game_dir: Path) -> dict[str, Lesson]:
    for dir in [roleplay_dir, vocabulary_game_dir]:
        if not dir.exists() or not dir.is_dir():
            raise ValueError(f"Directory {dir} does not exist or is not a directory.")

    roleplay_lesson_paths = [p for p in roleplay_dir.iterdir() if p.suffix == ".toml"]
    vocabulary_game_lesson_paths = [p for p in vocabulary_game_dir.iterdir() if p.suffix == ".toml"]

    # combine and load all lessons
    all_lesson_paths = roleplay_lesson_paths + vocabulary_game_lesson_paths
    lessons = {}
    for path in all_lesson_paths:
        lessons[path.stem] = load_lesson(path)

    return lessons