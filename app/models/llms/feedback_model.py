"""
Define how the model should behave, but not how to call it - that goes in feedback.py
"""
import tomllib
from pathlib import Path

from app.models.environments.lesson import Lesson
from app.models.environments.session import SessionConfig

FEEDBACK_CONFIG_DIR = Path(__file__).parents[2] / "data" / "feedback"

class FeedbackModel:
    def __init__(
        self,
        model_id: str,
        session_config: SessionConfig,
        lesson_config: Lesson | None = None,
        conversation: str | list[dict] | None = None,
    ):
        self.session_config = session_config
        self.lesson_config = lesson_config
        self.model_id: str = model_id
        self.temperature = 0.2
        self.conversation = conversation

        config_path = FEEDBACK_CONFIG_DIR / f"{session_config.language.lower()}.toml"
        with open(config_path, "rb") as f:
            self._prompts = tomllib.load(f)

        self.immediate_feedback_prompt = self._build_immediate_prompt()
        self.general_feedback_prompt = (
            self._build_general_prompt(conversation)
            if conversation is not None
            else ""
        )

    def _get_focus_line(self) -> str:
        # no lesson in free chat — fall back to communication focus
        if not self.lesson_config:
            return self._prompts["focus_lines"].get("communication", "")
        focus = self.lesson_config.lesson_feedback.feedback_focus
        if not focus:
            return ""
        return self._prompts["focus_lines"].get(focus, "")

    def _build_immediate_prompt(self) -> str:
        tmpl = self._prompts["immediate"]
        return tmpl["system_prompt"].format(
            language=self.session_config.language,
            level=self.session_config.user.proficiency_level,
            focus_line=self._get_focus_line(),
            example=tmpl["example"],
        )

    def _normalize_conversation(self, conversation: str | list[dict] | None) -> str:
        if conversation is None:
            return ""
        if isinstance(conversation, str):
            return conversation.strip()
        return "\n".join(
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in conversation
        ).strip()

    def _build_general_prompt(self, conversation: str | list[dict] | None = None) -> str:
        effective_conversation = self._normalize_conversation(conversation or self.conversation)
        if not effective_conversation:
            raise ValueError("Conversation history is required to build general feedback prompt.")

        tmpl = self._prompts["general"]
        return tmpl["system_prompt"].format(
            language=self.session_config.language,
            level=self.session_config.user.proficiency_level,
            focus_line=self._get_focus_line(),
            conversation=effective_conversation,
            example=tmpl["example"],
        )