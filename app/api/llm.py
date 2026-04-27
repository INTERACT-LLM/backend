"""
API for LLM provider and model configuration.
"""

from fastapi import APIRouter
from app.services.model_config import settings, available_models

router = APIRouter()


@router.get("/llm/models")
def get_models():
    return {
        "models": available_models(),
        "provider": settings.llm_provider,
        "default_model": settings.default_model,
    }


@router.get("/llm/status")
def get_status():
    base_url = (
        settings.ollama_base_url
        if settings.llm_provider == "ollama"
        else settings.vllm_base_url
    )
    return {
        "provider": settings.llm_provider,
        "base_url": base_url,
    }