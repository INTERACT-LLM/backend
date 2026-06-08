import os
from openai import OpenAI
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("APP_ENV"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # primary providers
    llm_provider: str
    ollama_base_url: str | None = None
    vllm_base_url: str | None = None
    available_models: str
    default_model: str | None = None

    # anthropic fallback
    anthropic_base_url: str | None = None
    anthropic_api_key: str | None = None
    anthropic_model: str | None = None
    claude_fallback_enabled: bool = False
    primary_recheck_interval_s: int = 300

    @model_validator(mode="after")
    def check_config(self):
        self.available_models = [m.strip() for m in self.available_models.split(",")]

        # if only one model, it's the default
        if len(self.available_models) == 1:
            self.default_model = self.available_models[0]

        url = getattr(self, f"{self.llm_provider}_base_url", None)
        if not url:
            raise ValueError(
                f"Provider is {self.llm_provider!r} but "
                f"{self.llm_provider}_base_url is not set."
            )
        if self.default_model and self.default_model not in self.available_models:
            raise ValueError(
                f"default_model {self.default_model!r} is not in "
                f"available_models: {self.available_models}"
            )

        # Fallback validation: if enabled, all Anthropic settings must be present.
        if self.claude_fallback_enabled:
            missing = [
                name for name, val in [
                    ("anthropic_base_url", self.anthropic_base_url),
                    ("anthropic_api_key", self.anthropic_api_key),
                    ("anthropic_model", self.anthropic_model),
                ] if not val
            ]
            if missing:
                raise ValueError(
                    f"claude_fallback_enabled is True but missing: {', '.join(missing)}"
                )
        return self


settings = Settings()


def available_models() -> list[str]:
    return settings.available_models


def active_model(model_id: str | None = None) -> str:
    resolved = model_id or settings.default_model
    if resolved not in settings.available_models:
        raise ValueError(
            f"Model {resolved!r} is not available for provider "
            f"{settings.llm_provider!r}. Available: {settings.available_models}"
        )
    return resolved


def get_client(provider: str, model_id: str | None = None) -> tuple[OpenAI, str]:
    """
    Return an OpenAI-compatible client for the given provider, plus the model id to use.
    """
    url = getattr(settings, f"{provider}_base_url", None)
    if not url:
        raise ValueError(f"No base_url configured for provider {provider!r}")

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise RuntimeError("anthropic_api_key is not set")
        client = OpenAI(base_url=url, api_key=settings.anthropic_api_key)
        return client, settings.anthropic_model

    # ollama or vllm
    resolved = active_model(model_id)
    return OpenAI(base_url=url, api_key="not-used"), resolved