"""
Add minimal LLM logic here
"""

from pathlib import Path
import ollama

# models
from app.models.data.chat import ChatMessage
from app.models.llms.chat_model import ChatModel

# services
from app.services.load_environments import load_lesson, load_session
from app.services.model_config import MODEL

sessions = {}

def handle_conversation(
    message: ChatMessage,
    lesson_id: str,
    session_id: str = "default",
) -> list[ChatMessage]:

    # load chat model
    session_config = load_session(session_path=Path(__file__).parents[2] / "app" / "data" / "session.toml")
    lesson = load_lesson(lesson_path=Path(__file__).parents[2] / "app" / "data" / "lessons" / f"{lesson_id}.toml")
    chat_model = ChatModel(session_config=session_config, lesson_config=lesson, model_id=MODEL)
        
    # intialize session if it doesn't exist, placing system prompt as first msg
    if session_id not in sessions: 
        sessions[session_id] = [
            ChatMessage(role="system", content=chat_model.system_prompt)
        ]

    # add user message
    sessions[session_id].append(message)

    # call model
    response = ollama.chat(
        model=chat_model.model_id,
        messages=[m.model_dump() for m in sessions[session_id]],
    )

    assistant = ChatMessage(
        role="assistant",
        content=response["message"]["content"]
    )

    sessions[session_id].append(assistant)

    return list(sessions[session_id])