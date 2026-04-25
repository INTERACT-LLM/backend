from pathlib import Path 
import tomllib
from app.models.environments.lesson import Lesson


def load_lesson(lesson_path: Path) -> Lesson:
    with open(lesson_path, "rb") as f:
        data = tomllib.load(f)  
    
    lesson = Lesson.model_validate(data)
    
    return lesson

def load_all_lessons(lesson_dir) -> dict[str, Lesson]:
    if not lesson_dir.exists() or not lesson_dir.is_dir():
        raise ValueError(f"Directory {lesson_dir} does not exist or is not a directory.")

    lesson_paths = [p for p in lesson_dir.iterdir() if p.suffix == ".toml"]

    lessons = {}
    for path in lesson_paths:
        lessons[path.stem] = load_lesson(path)

    return lessons