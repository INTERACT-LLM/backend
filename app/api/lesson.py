"""
API for getting lesson content and generating lesson plans based on user input.
"""
from pathlib import Path
import random
from fastapi import APIRouter, HTTPException, Query
from app.models.llms.chat_model import ChatModel
from app.models.llms.feedback_model import FeedbackModel
from app.models.environments.lesson import TabuInstructions, TwentyQuestionsInstructions
from app.services.game_utils import pick_secret_20Q
from app.services.load_lessons import load_all_lessons, load_lesson
from app.services.store_chat import get_chat

router = APIRouter()

LESSONS_DIR = Path(__file__).parents[2] / "app" / "data" / "lessons"


@router.get("/lessons")
async def get_lessons():
    lessons = load_all_lessons(LESSONS_DIR)
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


@router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str):
    lesson = load_lesson(lesson_path=LESSONS_DIR / f"{lesson_id}.toml")
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson.model_dump()


@router.get("/lessons/{lesson_id}/game-state")
async def get_game_state(lesson_id: str, chat_id: str = Query(...)):
    lesson = load_lesson(lesson_path=LESSONS_DIR / f"{lesson_id}.toml")
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    instructions = lesson.lesson_instructions

    if isinstance(instructions, TabuInstructions):
        secret = random.choice(instructions.vocabulary)
        return {
            "game_type": "tabu",
            "secret_word": secret.word,
            "forbidden_words": secret.forbidden_words,
        }

    if isinstance(instructions, TwentyQuestionsInstructions):
        secret = pick_secret_20Q(instructions.vocabulary, chat_id)
        return {
            "game_type": "twenty_questions",
            "secret_word": secret,
            "max_questions": instructions.max_questions,
        }

    raise HTTPException(status_code=400, detail="Lesson is not a vocabulary game")


@router.get("/lessons/{lesson_id}/prompts")
async def get_system_prompts(lesson_id: str, chat_id: str = Query(...)):
    if lesson_id == "undefined" or not lesson_id:
        raise HTTPException(status_code=400, detail="lesson_id is required")
    if chat_id == "undefined" or not chat_id:
        raise HTTPException(status_code=400, detail="chat_id is required")

    chat_state = get_chat(chat_id)
    lesson = load_lesson(lesson_path=LESSONS_DIR / f"{lesson_id}.toml")

    if not lesson or not chat_state:
        raise HTTPException(status_code=404, detail="Lesson or chat not found")

    chat_model = ChatModel(
        session_config=chat_state.snapshotted_config,
        lesson_config=lesson,
        model_id="llama-3.2",
    )
    immediate_feedback_model = FeedbackModel(
        model_id="llama-3.2",
        session_config=chat_state.snapshotted_config,
        lesson_config=lesson,
    )

    return {
        "chat_system_prompt": chat_model.system_prompt,
        "immediate_feedback_prompt": immediate_feedback_model.immediate_feedback_prompt,
    }