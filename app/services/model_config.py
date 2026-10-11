import os
from functools import lru_cache

import httpx
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
    default_model: str

    # anthropic fallback
    anthropic_base_url: str | None = None
    anthropic_api_key: str | None = None
    anthropic_model: str | None = None
    claude_fallback_enabled: bool = False
    primary_recheck_interval_s: int = 300

    # LLM request limits (can be overridden in the env file)
    # connect: wait for the provider to answer at all. Short, so a dead provider
    #          is noticed fast and failover starts.
    # read:    wait for the next piece of data. While streaming, the gap between
    #          tokens. For feedback (not streamed), the whole answer.
    llm_connect_timeout_s: float = 5.0
    llm_read_timeout_s: float = 90.0
    llm_max_retries: int = 1  # OpenAI default is 2

    @model_validator(mode="after")
    def check_config(self):
        url = getattr(self, f"{self.llm_provider}_base_url", None)
        if not url:
            raise ValueError(
                f"Provider is {self.llm_provider!r} but "
                f"{self.llm_provider}_base_url is not set."
            )

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


@lru_cache
def _build_client(provider: str) -> OpenAI:
    """
    Build the client for one provider. Thanks to lru_cache, this runs once per
    provider, and every later call returns the same client, which reuses its
    open connections. OpenAI clients are safe to share between threads.
    """
    url = getattr(settings, f"{provider}_base_url", None)
    if not url:
        raise ValueError(f"No base_url configured for provider {provider!r}")

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise RuntimeError("anthropic_api_key is not set")
        api_key = settings.anthropic_api_key
    else:
        api_key = "not-used"

    return OpenAI(
        base_url=url,
        api_key=api_key,
        timeout=httpx.Timeout(settings.llm_read_timeout_s, connect=settings.llm_connect_timeout_s),
        max_retries=settings.llm_max_retries,
    )


def get_client(provider: str) -> tuple[OpenAI, str]:
    """
    Return an OpenAI-compatible client for the given provider, plus the model id to use.
    The client is shared (see _build_client), so calling this often is cheap.
    """
    client = _build_client(provider)
    model = settings.anthropic_model if provider == "anthropic" else settings.default_model
    return client, model