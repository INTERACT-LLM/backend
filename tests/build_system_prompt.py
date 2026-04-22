from pathlib import Path

from app.services.load_environments import load_lesson, load_session

from app.models.llms.chat_model import ChatModel
from app.models.llms.feedback_model import FeedbackModel

if __name__ == "__main__":
    # quick test to print out the generated prompts
    session_config = load_session(session_path=Path(__file__).parents[1] / "app" / "data" / "session.toml")
    lesson = load_lesson(lesson_path=Path(__file__).parents[1] / "app" / "data" / "lessons" / f"game_20questions.toml")

    chat_model = ChatModel(session_config=session_config, lesson_config=lesson, model_id="llama-3.2")
    immediate_feedback_model = FeedbackModel(model_id="llama-3.2", session_config=session_config, lesson_config=lesson)
    
    general_feedback_model = FeedbackModel(model_id="llama-3.2", session_config=session_config, lesson_config=lesson, conversation=[{"role": "user", "content": "Hola, ¿cómo estás?"}, {"role": "assistant", "content": "Estoy bien, gracias. ¿Y tú?"}, {"role": "user", "content": "Muy bien también. ¿Qué hiciste hoy?"}])

    print("=== CHAT MODEL SYSTEM PROMPT ===")
    print(chat_model.system_prompt)
    print("\n\n=== IMMEDIATE FEEDBACK PROMPT ===")
    print(immediate_feedback_model.immediate_feedback_prompt)
    print("\n\n=== GENERAL FEEDBACK PROMPT ===")
    print(general_feedback_model.general_feedback_prompt)