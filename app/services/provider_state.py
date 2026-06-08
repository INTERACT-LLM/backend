"""
Runtime state for which LLM provider is currently serving requests.

Configured provider lives in settings (immutable after boot).
Active provider lives here and flips on failover/failback.
"""
import asyncio
import time
from typing import Literal

from app.services.model_config import settings

ProviderName = Literal["ollama", "vllm", "anthropic"]


class ProviderState:
    def __init__(self):
        self._primary: ProviderName = settings.llm_provider
        self._active: ProviderName = settings.llm_provider
        self._primary_last_failure_ts: float | None = None
        self._lock = asyncio.Lock()

    @property
    def primary(self) -> ProviderName:
        return self._primary

    @property
    def active(self) -> ProviderName:
        return self._active

    @property
    def is_failed_over(self) -> bool:
        return self._active != self._primary

    @property
    def primary_last_failure_ts(self) -> float | None:
        return self._primary_last_failure_ts

    async def mark_primary_failed(self) -> None:
        if not settings.claude_fallback_enabled:
            return
        async with self._lock:
            if self._active != "anthropic":
                self._active = "anthropic"
                self._primary_last_failure_ts = time.time()
                print(f"[ProviderState] Failed over: {self._primary} -> anthropic")

    async def mark_primary_recovered(self) -> None:
        async with self._lock:
            if self._active != self._primary:
                self._active = self._primary
                self._primary_last_failure_ts = None
                print(f"[ProviderState] Recovered: anthropic -> {self._primary}")


provider_state = ProviderState()