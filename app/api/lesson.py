"""
API for getting lesson content and generating lesson plans based on user input.
"""
from fastapi import APIRouter
from app.models.lesson import Lesson

router = APIRouter()


initial_system_prompt = "You are a language tutor, speaking only Spanish!"
LESSONS = [
    Lesson(
        id="game",
        ui_title="💬 20 Questions Game",
        ui_lesson_description="A fun guessing game to practice conversation skills.",
        initial_system_prompt=initial_system_prompt,
        scenario="Open conversation",
    ),
    Lesson(
        id="roleplay",
        ui_title="🧑‍🍳 Roleplay. Ordering at a Restaurant",
        ui_lesson_description="Practice a common real-world scenario.",
        initial_system_prompt=initial_system_prompt,
        scenario="Help with coding problems",
        feedback_focus="communication",
    ),
]

@router.get("/lessons")
async def get_lessons():
    return {"lessons": [lesson.model_dump() for lesson in LESSONS]}