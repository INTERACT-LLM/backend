from pathlib import Path
from app.services.lessons.load_lessons import load_all_lessons

if __name__ == "__main__":
    path = Path(__file__).resolve()
    roleplay_dir = path.parents[1] / "app" / "data" / "lessons" / "roleplay"
    vocabulary_game_dir = (
        path.parents[1] / "app" / "data" / "lessons" / "vocabulary_game"
    )

    lessons = load_all_lessons(roleplay_dir, vocabulary_game_dir)
    
    for lesson_id, lesson in lessons.items():
        print(f"Loaded lesson: {lesson_id} with type {lesson.lesson_type}")
        print(f"User instructions: {lesson.user_instructions}")
        print(f"Model instructions: {lesson.model_instructions}")
        print("-" * 40)