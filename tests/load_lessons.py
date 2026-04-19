from pathlib import Path
from app.services.lessons.load_lessons import load_all_lessons

if __name__ == "__main__":
    path = Path(__file__)
    lessons_dir = path.parents[1] / "app" / "data" / "lessons"

    lessons = load_all_lessons(lessons_dir)

    for lesson_id, lesson in lessons.items():
        print(f"Loaded lesson: {lesson_id} with type {lesson.lesson_type}. Number of turns: {lesson.min_turns}")
        print(f"User instructions: {lesson.user_instructions}")
        print(f"Model instructions: {lesson.model_instructions}")
        print("-" * 40)