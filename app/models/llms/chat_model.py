"""
Defines how the chat model should behave — config and prompt building only.
No ollama calls — IO lives in services/llm.py.
"""
import random
import tomllib
from pathlib import Path

from app.models.environments.session import SessionConfig
from app.models.environments.lesson import Lesson

CHAT_CONFIG_PATH = Path(__file__).parents[2] / "data" / "chat.toml"

class ChatModel:
    """
    Holds chat model config and builds the system prompt from:
      - data/chat.toml               (static base system prompt)
      - session_config               (user facts)
      - lesson_config                (lesson-specific instructions)
    """

    def __init__(
        self,
        session_config: SessionConfig,
        lesson_config: Lesson,
        model_id: str = "llama3.2:3b",
        temperature: float = 0.7,
    ):
        self.session_config = session_config
        self.lesson_config = lesson_config
        self.model_id = model_id
        self.temperature = temperature

        with open(CHAT_CONFIG_PATH, "rb") as f:
            self._chat_config = tomllib.load(f)

        self.system_prompt = self._build_system_prompt()

    ## PROMPT BUILDING ##
    def _build_system_prompt(self) -> str:
        session = self.session_config
        lesson = self.lesson_config

        # base prompt from chat.toml — language only, no lesson context
        base = self._chat_config["system_prompt"].format(
            language=session.language,
        )

        general_parts = [
            "GENERAL INSTRUCTIONS:",
            f"You are teaching the language: {session.language}",
        ]
        if session.user.proficiency_level:
            general_parts.append(f"Student level is: {session.user.proficiency_level}")
        if session.user.preferences:
            general_parts.append(
                f"Here is some information about the student's preferences: {session.user.preferences}"
            )

        ## LESSON ## (note feedback focus is not added here!)
        lesson_instructions = lesson.lesson_instructions
        lesson_block_parts = [
            "LESSON-SPECIFIC INSTRUCTIONS:",
            f"The lesson type is: {lesson.lesson_type}",
            "This is the task scenario that you need to facilitate:\n"
            f"{lesson_instructions.scenario}",
        ]

        if lesson_instructions.cultural_contexts:
            lesson_block_parts.append(
                f"Cultural context: {'; '.join(lesson_instructions.cultural_contexts)}"
            )

        vocabulary_block = self._build_vocabulary_block()

        general = "\n\n".join(general_parts)
        lesson_block = "\n\n".join(lesson_block_parts)
        
        return "\n\n".join(filter(None, [base, general, lesson_block, vocabulary_block])).strip()

    def _build_vocabulary_block(self) -> str:
        lesson_instructions = self.lesson_config.lesson_instructions

        if not lesson_instructions.vocabulary:
            return ""

        match self.lesson_config.lesson_type:
            case "roleplay":
                return (
                    "Incorporate these words naturally: "
                    f"{', '.join(lesson_instructions.vocabulary)}"
                )
            case "vocabulary_game":
                max_questions = getattr(lesson_instructions, "max_questions", 20)
                return (
                    f"Secret word: {random.choice(lesson_instructions.vocabulary)}. "
                    f"Guide the student to guess it in up to {max_questions} questions."
                )
            case _:
                return ""