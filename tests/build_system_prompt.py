from pathlib import Path

from app.models.data.chat import ChatConfig  
from app.models.environments.user import UserProfile  
from app.services.load_lessons import load_lesson

from app.models.llms.chat_model import ChatModel
from app.models.llms.feedback_model import FeedbackModel

if __name__ == "__main__":
    # quick test to print out the generated prompts
    LESSON_ID = "game_tabu"  
    CHAT_ID = "test-chat"    

  
    config = ChatConfig(
        lesson_id=LESSON_ID,
        tutor_starts=False,
        provider="ollama",
        model="llama3.2:3b",
        user=UserProfile(name="Mina", language="Spanish", proficiency_level="intermediate"),
    )
    lesson = load_lesson(lesson_path=Path(__file__).parents[1] / "app" / "data" / "lessons" / f"{LESSON_ID}.toml")

    chat_model = ChatModel(config=config, chat_id=CHAT_ID, lesson_config=lesson, model_id=config.model)  
    immediate_feedback_model = FeedbackModel(model_id=config.model, config=config, lesson_config=lesson)  

    general_feedback_model = FeedbackModel(model_id=config.model, config=config, lesson_config=lesson, conversation=[{"role": "user", "content": "Hola, ¿cómo estás?"}, {"role": "assistant", "content": "Estoy bien, gracias. ¿Y tú?"}, {"role": "user", "content": "Muy bien también. ¿Qué hiciste hoy?"}])  # CHANGED

    print("=== CHAT MODEL SYSTEM PROMPT ===")
    print(chat_model.system_prompt)
    print("\n\n=== IMMEDIATE FEEDBACK PROMPT ===")
    print(immediate_feedback_model.immediate_feedback_prompt)
    print("\n\n=== GENERAL FEEDBACK PROMPT ===")
    print(general_feedback_model.general_feedback_prompt)