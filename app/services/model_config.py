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

    llm_provider: str
    ollama_base_url: str | None = None
    vllm_base_url: str | None = None
    available_models: str
    default_model: str | None = None

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


def get_client(model_id: str | None = None) -> tuple[OpenAI, str]:
    resolved = active_model(model_id)
    url = getattr(settings, f"{settings.llm_provider}_base_url")
    return OpenAI(base_url=url, api_key="not-used"), resolved