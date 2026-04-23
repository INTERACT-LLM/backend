"""
API for getting lesson content and generating lesson plans based on user input.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.models.llms.chat_model import ChatModel
from app.models.llms.feedback_model import FeedbackModel
from app.services.load_environments import load_all_lessons, load_lesson, load_session

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
                "min_turns": l.min_turns,
                **l.lesson_presentation.model_dump(),
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
    return lesson.model_dump()

@router.get("/lessons/{lesson_id}/prompts")
async def get_system_prompts(lesson_id: str):
    session_config = load_session(session_path=Path(__file__).parents[2] / "app" / "data" / "session.toml")
    lesson = load_lesson(lesson_path=Path(__file__).parents[2] / "app" / "data" / "lessons" / f"{lesson_id}.toml")

    if not lesson and not session_config:
        raise HTTPException(status_code=404, detail="Lesson and session config not found")
    
    chat_model = ChatModel(session_config=session_config, lesson_config=lesson, model_id="llama-3.2")
    immediate_feedback_model = FeedbackModel(model_id="llama-3.2", session_config=session_config, lesson_config=lesson)

    return {
        "chat_system_prompt": chat_model.system_prompt,
        "immediate_feedback_prompt": immediate_feedback_model.immediate_feedback_prompt,
    }