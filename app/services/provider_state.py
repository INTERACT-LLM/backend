"""
Runtime state for which LLM provider is currently serving requests.

Configured provider lives in settings (immutable after boot).
Two runtime facts live here:
  - primary_online: did the primary respond at the last check or request?
  - active: which provider new chats bind to (flips on failover/failback)
They are separate on purpose: with the fallback disabled, the primary can be
offline while active still points at it.

The flips are plain (not async) and guarded by a threading.Lock, so they work
both from worker threads (failing chat streams) and from async code (health monitor).
Nothing inside the lock waits on anything, so holding it from async code is fine.
Both mark_ methods are safe to call repeatedly; they only print on a real change.
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
        self._primary_online: bool = True  # assumed until the first check says otherwise
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
    def primary_online(self) -> bool:
        return self._primary_online

    @property
    def is_failed_over(self) -> bool:
        return self._active != self._primary

    @property
    def primary_last_failure_ts(self) -> float | None:
        return self._primary_last_failure_ts

    def mark_primary_failed(self) -> None:
        """
        Record that the primary is offline, and switch to anthropic if the fallback is enabled.
        Safe to call from many threads at once.
        """
        with self._lock:
            if self._primary_online:
                self._primary_online = False
                self._primary_last_failure_ts = time.time()
                print(f"[ProviderState] Primary offline: {self._primary}")

            if settings.claude_fallback_enabled and self._active != "anthropic":
                self._active = "anthropic"
                print(f"[ProviderState] Failed over: {self._primary} -> anthropic")

    def mark_primary_recovered(self) -> None:
        """Record that the primary is online again, and switch back to it."""
        with self._lock:
            if not self._primary_online:
                self._primary_online = True
                self._primary_last_failure_ts = None
                print(f"[ProviderState] Primary online: {self._primary}")

            if self._active != self._primary:
                self._active = self._primary
                print(f"[ProviderState] Recovered: anthropic -> {self._primary}")


provider_state = ProviderState()