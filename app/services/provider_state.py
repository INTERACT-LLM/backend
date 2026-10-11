"""
Runtime state for which LLM provider is currently serving requests.

Configured provider lives in settings (immutable after boot).
Active provider lives here and flips on failover/failback.

The flips are plain (not async) and guarded by a threading.Lock, so they work
both from worker threads (failing chat streams) and from async code (health monitor).
Nothing inside the lock waits on anything, so holding it from async code is fine.
"""
import threading
import time
from typing import Literal

from app.services.model_config import settings

ProviderName = Literal["ollama", "vllm", "anthropic"]


class ProviderState:
    def __init__(self):
        self._primary: ProviderName = settings.llm_provider
        self._active: ProviderName = settings.llm_provider
        self._primary_last_failure_ts: float | None = None
        # threading.Lock, not asyncio.Lock: failing streams call this from worker threads
        self._lock = threading.Lock()

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

    def mark_primary_failed(self) -> None:
        """Switch to anthropic. Safe to call from many threads at once; only the first switches."""
        if not settings.claude_fallback_enabled:
            return
        with self._lock:
            if self._active != "anthropic":
                self._active = "anthropic"
                self._primary_last_failure_ts = time.time()
                print(f"[ProviderState] Failed over: {self._primary} -> anthropic")

    def mark_primary_recovered(self) -> None:
        """Switch back to the primary."""
        with self._lock:
            if self._active != self._primary:
                self._active = self._primary
                self._primary_last_failure_ts = None
                print(f"[ProviderState] Recovered: anthropic -> {self._primary}")


provider_state = ProviderState()