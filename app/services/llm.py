"""
Add minimal LLM logic here
"""

import ollama
from app.data.lessons import LESSONS
from app.models.chat import ChatMessage
from app.data.default_system_prompt import DEFAULT_SYSTEM_PROMPT
from app.models.lesson import build_system_prompt

MODEL = "smollm:1.7b"

sessions = {}

def handle_conversation(
    message: ChatMessage,
    session_id: str = "default",
    lesson_id: str | None = None,
) -> list[ChatMessage]:

    if session_id not in sessions: # new session, initialize with system prompt (with/without lesson-specific prompt)
        lesson = LESSONS.get(lesson_id)

        if lesson:
            system_prompt = build_system_prompt(lesson)
        else: 
            system_prompt = DEFAULT_SYSTEM_PROMPT

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