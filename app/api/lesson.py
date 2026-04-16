"""
API for getting lesson content and generating lesson plans based on user input.
"""
from fastapi import APIRouter
from app.data.lessons import LESSONS

router = APIRouter()

@router.get("/lessons")
async def get_lessons():
    return {
        "lessons": [
            {
                "id": l.id,
                "ui_title": l.ui_title,
                "ui_lesson_description": l.ui_lesson_description,
            }
            for l in LESSONS.values()
        ]
    }