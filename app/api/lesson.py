"""
API for getting lesson content and generating lesson plans based on user input.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.services.lessons.load_lessons import load_all_lessons, load_lesson

router = APIRouter()

LESSONS_DIR = Path(__file__).parents[2] / "app" / "data" / "lessons"

@router.get("/lessons")
async def get_lessons():
    lessons = load_all_lessons(LESSONS_DIR)
    # api "envelope" response : see https://jsonapi.org/
    return {
        "lessons": [
            {
                "id": l.id,
                "lesson_type": l.lesson_type,
                **l.user_instructions.model_dump(),
            }
            for l in lessons.values()
        ]
    }

# for getting lesson details fro a specific lesson
@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    lesson = load_lesson(lesson_path=Path(__file__).parents[2] / "app" / "data" / "lessons" / f"{lesson_id}.toml")
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"id": lesson.id, "lesson_type": lesson.lesson_type, **lesson.user_instructions.model_dump()}

@router.get("/lessons/{lesson_id}/details")
async def get_lesson_details(lesson_id: str, lesson_type: str):
    lesson = load_lesson(lesson_path=Path(__file__).parents[2] / "app" / "data" / "lessons" / lesson_type / f"{lesson_id}.toml")
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    mi = lesson.model_instructions
    return {
        "id": lesson.id,
        **lesson.user_instructions.model_dump(),
        "feedback_focus": mi.feedback_focus,
        "cultural_contexts": mi.cultural_contexts,
        "min_turns": mi.min_turns,
        "lesson_type": lesson.lesson_type,
    }