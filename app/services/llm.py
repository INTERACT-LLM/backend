"""
Add minimal LLM logic here
"""

import ollama
from app.models.chat import ChatMessage

MODEL = "smollm:1.7b"
SYSTEM_PROMPT = "You are a helpful assistant."

sessions = {}

def handle_conversation(
    message: ChatMessage,
    session_id: str = "default",
    lesson_id: str | None = None,
) -> list[ChatMessage]:

    if session_id not in sessions:
        if lesson_id is None:
            system_prompt = SYSTEM_PROMPT
        else: 
            system_prompt = SYSTEM_PROMPT + f" Lesson ID: {lesson_id}" # placeholder for now, will build out system prompt based on lesson details later

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