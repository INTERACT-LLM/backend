"""
Defines how the chat model should behave — config and prompt building only.
No LLM calls — IO lives in services/chat.py.
"""
import tomllib
from pathlib import Path

from app.models.environments.session import SessionConfig
from app.models.environments.lesson import Lesson
from app.services.game_utils import pick_secret_20Q

DATA_DIR = Path(__file__).parents[2] / "data"
CHAT_CONFIG_PATH = DATA_DIR / "chat.toml"
FREE_CHAT_CONFIG_PATH = DATA_DIR / "free_chat.toml"


class ChatModel:
    """
    Holds chat model config and builds the system prompt from:
      - data/chat.toml or data/free_chat.toml  (base system prompt)
      - session_config                          (user facts)
      - lesson_config                           (lesson-specific instructions, optional)
    """

    def __init__(
        self,
        session_config: SessionConfig,
        lesson_config: Lesson | None = None,
        model_id: str = "llama3.2:3b",
        temperature: float = 0.7,
    ):
        self.session_config = session_config
        self.lesson_config = lesson_config
        self.model_id = model_id
        self.temperature = temperature

        config_path = CHAT_CONFIG_PATH if lesson_config else FREE_CHAT_CONFIG_PATH
        with open(config_path, "rb") as f:
            self._chat_config = tomllib.load(f)

        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        session = self.session_config

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

        general = "\n\n".join(general_parts)

        if self.lesson_config is None:
            return "\n\n".join(filter(None, [base, general])).strip()

        lesson_instructions = self.lesson_config.lesson_instructions
        lesson_block_parts = [
            "LESSON-SPECIFIC INSTRUCTIONS:",
            f"The lesson type is: {self.lesson_config.lesson_type}",
            "This is the task scenario that you need to facilitate:\n"
            f"{lesson_instructions.scenario}",
        ]

        if lesson_instructions.cultural_contexts:
            lesson_block_parts.append(
                f"Cultural context: {'; '.join(lesson_instructions.cultural_contexts)}"
            )

        vocabulary_block = self._build_vocabulary_block()
        lesson_block = "\n\n".join(lesson_block_parts)

        return "\n\n".join(filter(None, [base, general, lesson_block, vocabulary_block])).strip()

    def _build_vocabulary_block(self) -> str:
        if self.lesson_config is None:
            return ""

        from app.models.environments.lesson import (
            RoleplayInstructions,
            TwentyQuestionsInstructions,
            TabuInstructions,
        )

        lesson_instructions = self.lesson_config.lesson_instructions

        if not lesson_instructions.vocabulary:
            return ""

        match lesson_instructions:
            case RoleplayInstructions():
                return (
                    "Incorporate these words naturally: "
                    f"{', '.join(lesson_instructions.vocabulary)}"
                )
            case TwentyQuestionsInstructions():
                secret_word = pick_secret_20Q(
                    lesson_instructions.vocabulary,
                    self.session_config.session_id
                )
                return (
                    f"Secret word: {secret_word}. "
                    f"Guide the student to guess it in up to {lesson_instructions.max_questions} questions."
                )
            case _:
                return ""