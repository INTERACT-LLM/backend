"""
API for getting lesson content and generating lesson plans based on user input.
"""
from pathlib import Path
import random
from fastapi import APIRouter, HTTPException, Query
from app.models.llms.chat_model import ChatModel
from app.models.llms.feedback_model import FeedbackModel
from app.models.environments.lesson import TabuInstructions
from app.services.load_lessons import load_all_lessons, load_lesson
from app.services.session_store import get_session

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
    lesson = load_lesson(lesson_path= LESSONS_DIR / f"{lesson_id}.toml")
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson.model_dump()

@router.get("/lessons/{lesson_id}/game-state")
async def get_game_state(lesson_id: str):
    lesson = load_lesson(lesson_path=LESSONS_DIR / f"{lesson_id}.toml")
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    instructions = lesson.lesson_instructions
    if not isinstance(instructions, TabuInstructions):
        raise HTTPException(status_code=400, detail="Lesson is not a Tabu game")
    
    secret = random.choice(instructions.vocabulary)
    return {
        "secret_word": secret.word,
        "forbidden_words": secret.forbidden_words
    }

@router.get("/lessons/{lesson_id}/prompts")
async def get_system_prompts(lesson_id: str, session_id: str = Query(...)):
    # Validate that lesson_id and session_id are not undefined
    if lesson_id == "undefined" or not lesson_id:
        raise HTTPException(status_code=400, detail="lesson_id is required and cannot be undefined")
    if session_id == "undefined" or not session_id:
        raise HTTPException(status_code=400, detail="session_id is required and cannot be undefined")
    
    session_config = get_session(session_id)
    lesson = load_lesson(lesson_path=LESSONS_DIR / f"{lesson_id}.toml")

    if not lesson or not session_config:
        raise HTTPException(status_code=404, detail="Lesson and session config not found")
    
    chat_model = ChatModel(session_config=session_config, lesson_config=lesson, model_id="llama-3.2")
    immediate_feedback_model = FeedbackModel(model_id="llama-3.2", session_config=session_config, lesson_config=lesson)

    return {
        "chat_system_prompt": chat_model.system_prompt,
        "immediate_feedback_prompt": immediate_feedback_model.immediate_feedback_prompt,
    }