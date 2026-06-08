"""
Background task that monitors primary provider health and updates ProviderState.

Pings the configured primary on a schedule. Anthropic is never pinged. 
Anthropic's health is only discovered when a real chat attempts to use it (since it would cost money and it is a fallback.)
"""
import asyncio

import httpx

from app.services.model_config import settings
from app.services.provider_state import provider_state


def _primary_health_url() -> str:
    """Build the health URL for the configured primary provider."""
    if settings.llm_provider == "ollama":
        base_url = settings.ollama_base_url
        return f"{base_url.removesuffix('/v1')}/api/version"
    # vllm
    return f"{settings.vllm_base_url}/models"


async def _check_primary_once() -> bool:
    """Return True if the primary responds 200, False otherwise."""
    url = _primary_health_url()
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url)
        return resp.status_code == 200
    except Exception:
        return False


async def monitor_primary_health() -> None:
    """
    Long-running loop: ping primary, update ProviderState, sleep, repeat.
    Cancelled by FastAPI's lifespan on shutdown.
    """
    interval = settings.primary_recheck_interval_s
    print(f"[health_monitor] Started, interval={interval}s, primary={provider_state.primary}")

    try:
        while True:
            online = await _check_primary_once()

            if online and provider_state.is_failed_over:
                await provider_state.mark_primary_recovered()
            elif not online and not provider_state.is_failed_over:
                # Primary is down but we haven't failed over yet
                # (e.g., no user request has triggered it). Flip proactively.
                await provider_state.mark_primary_failed()

            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        print("[health_monitor] Stopped.")
        raise