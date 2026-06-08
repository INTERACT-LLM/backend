"""
API for LLM provider and model configuration.
"""
from fastapi import APIRouter

from app.services.model_config import settings, available_models
from app.services.provider_state import provider_state

router = APIRouter()


@router.get("/llm/models")
def get_models():
    return {
        "models": available_models(),
        "provider": settings.llm_provider,
        "default_model": settings.default_model,
    }


@router.get("/llm/status")
async def get_status():
    """
    Report current provider state. Reads from ProviderState (kept fresh by the
    background health monitor) — no live HTTP probing here.
    """
    return {
        "configured_provider": provider_state.primary,
        "active_provider":     provider_state.active,
        "is_failed_over":      provider_state.is_failed_over,
        "primary_online":      not provider_state.is_failed_over,
        "fallback_available":  settings.claude_fallback_enabled,
        "fallback_model":      settings.anthropic_model if settings.claude_fallback_enabled else None,
    }