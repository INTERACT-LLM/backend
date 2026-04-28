from openai import OpenAI
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROVIDER_MODELS: dict[str, list[str]] = {
    "ollama": [
        "llama3.2:3b",
        "smollm2:360m",
    ],
    "vllm": [
        "meta-llama/Llama-3.1-8B",
        "Qwen/Qwen3-0.6B",
    ],
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None)

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    vllm_base_url: str = "http://localhost:8000"
    default_model: str = "llama3.2:3b"

    @model_validator(mode='after')
    def check_default_model(self):
        allowed = PROVIDER_MODELS.get(self.llm_provider, [])
        if self.default_model not in allowed:
            raise ValueError(
                f"default_model {self.default_model!r} is not in PROVIDER_MODELS[{self.llm_provider!r}]: {allowed}"
            )
        return self


settings = Settings()


def available_models() -> list[str]:
    """Return models available for the currently active provider."""
    return PROVIDER_MODELS.get(settings.llm_provider, [])


def active_model(model_id: str | None = None) -> str:
    resolved = model_id or settings.default_model
    allowed = available_models()
    if resolved not in allowed:
        raise ValueError(
            f"Model {resolved!r} is not available on provider {settings.llm_provider!r}. "
            f"Available: {allowed}"
        )
    return resolved


def get_client(model_id: str | None = None) -> tuple[OpenAI, str]:
    """Return an OpenAI-compatible client and validated model name."""
    resolved = active_model(model_id)
    if settings.llm_provider == "ollama":
        return OpenAI(base_url=settings.ollama_base_url, api_key="not-used"), resolved
    elif settings.llm_provider == "vllm":
        return OpenAI(base_url=settings.vllm_base_url, api_key="not-used"), resolved
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider!r}. Use 'ollama' or 'vllm'.")