"""
API for getting lesson content and generating lesson plans based on user input.
"""
from fastapi import APIRouter
from app.models.lesson import Lesson

router = APIRouter()

LESSONS = [
    Lesson(
        id="general",
        name="💬 General Chat",
        initial_system_prompt="You are a helpful assistant.",
        scenario="Open conversation",
    ),
    Lesson(
        id="code",
        name="💻 Code Chat",
        initial_system_prompt="You are a programming tutor.",
        scenario="Help with coding problems",
        feedback_focus="communication",
    ),
]

@router.get("/lessons")
async def get_lessons():
    return {"lessons": [lesson.model_dump() for lesson in LESSONS]}