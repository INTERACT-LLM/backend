"""
Add minimal LLM logic here
"""

from pathlib import Path
import ollama
from app.models.chat import ChatMessage

from app.services.lessons.build_system_prompt import build_system_prompt
from app.services.lessons.load_general import load_general_instructions
from app.services.lessons.load_lessons import load_lesson


from app.services.model_config import MODEL

sessions = {}

def handle_conversation(
    message: ChatMessage,
    lesson_id: str,
    session_id: str = "default",
) -> list[ChatMessage]:

    if session_id not in sessions: # new session, initialize with system prompt (with/without lesson-specific prompt)
        lesson = load_lesson(lesson_path=Path(__file__).parents[2] / "app" / "data" / "lessons" / f"{lesson_id}.toml")
        general_instructions = load_general_instructions()
        system_prompt = build_system_prompt(lesson, general_instructions)

        sessions[session_id] = [
            ChatMessage(role="system", content=system_prompt)
        ]

    # add user message
    sessions[session_id].append(message)

    # call model
    response = ollama.chat(
        model=MODEL,
        messages=[m.model_dump() for m in sessions[session_id]],
    )

    assistant = ChatMessage(
        role="assistant",
        content=response["message"]["content"]
    )

    sessions[session_id].append(assistant)

    return list(sessions[session_id])