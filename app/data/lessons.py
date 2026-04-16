from app.models.lesson import Lesson
from app.data.default_system_prompt import DEFAULT_SYSTEM_PROMPT

LESSONS = {
    "game": Lesson(
        id="game",
        ui_title="💬 20 Questions Game",
        ui_lesson_description="A fun guessing game to practice conversation skills.",
        initial_system_prompt=DEFAULT_SYSTEM_PROMPT,
        scenario="Your name is Miguel and you should try to make the user guess that your object is a pineapple by only answering yes or no questions. The user will ask you questions to try to guess the object you are thinking of. You should only respond with 'yes' or 'no' and nothing else.",
    ),
    "roleplay": Lesson(
        id="roleplay",
        ui_title="🧑‍🍳 Roleplay. Ordering at a Restaurant",
        ui_lesson_description="Practice a common real-world scenario.",
        initial_system_prompt=DEFAULT_SYSTEM_PROMPT,
        scenario="Ordering food at a restaurant",
        feedback_focus="communication",
    ),
}