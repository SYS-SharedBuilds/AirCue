"""Abstract asynchronous LLM client interface and normalized completion result."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CompletionResult:
    """Normalized completion result returned across all LLM providers."""
    text: str
    model: str
    latency_s: float
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str = "stop"
    raw_error: str | None = None
    cost_usd: float = 0.0


class LLMClient(ABC):
    """Abstract interface for LLM calls."""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 150,
    ) -> CompletionResult:
        """Execute completion and return standardized CompletionResult."""
