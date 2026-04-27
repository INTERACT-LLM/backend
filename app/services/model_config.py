from openai import OpenAI
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434/v1"
    vllm_base_url: str = "http://localhost:8000/v1"
    ollama_model: str = "llama3.2:3b"
    vllm_model: str = "meta-llama/Meta-Llama-3.2-3B-Instruct"

    class Config:
        env_file = ".env.local" # fallback env file for development, can be overridden by .env.prod in production


settings = Settings()
print(f"[INFO:] Running with setup {settings.model_dump()}")

def active_model() -> str:
    """Return the model name for the currently active provider."""
    return settings.ollama_model if settings.llm_provider == "ollama" else settings.vllm_model


def get_client() -> tuple[OpenAI, str]:
    """Return an OpenAI-compatible client and model name for the active provider."""
    if settings.llm_provider == "ollama":
        return OpenAI(base_url=settings.ollama_base_url, api_key="not-used"), settings.ollama_model
    elif settings.llm_provider == "vllm":
        return OpenAI(base_url=settings.vllm_base_url, api_key="not-used"), settings.vllm_model
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider!r}. Use 'ollama' or 'vllm'.")