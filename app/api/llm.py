"""
API for LLM provider and model configuration.
"""

from fastapi import APIRouter
import httpx
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
async def get_status():
    if settings.llm_provider == "ollama":
        base_url = settings.ollama_base_url
        health_url = f"{base_url.rstrip('/')}/api/version"
    else:
        base_url = settings.vllm_base_url
        health_url = f"{base_url.rstrip('/')}/v1/models"
 
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(health_url)
        online = resp.status_code == 200
    except Exception:
        online = False

    print(f"Checked LLM status at {health_url}: online={online}")
 
    return {
        "provider": settings.llm_provider,
        "base_url": base_url,
        "online": online,
    }