"""Deterministic MockClient for offline testing of benchmark pipelines."""
from __future__ import annotations

import random

from aircue.llm.base import CompletionResult, LLMClient


class MockClient(LLMClient):
    """Deterministic mock client returning plausible announcements and decisions.

    Deliberately injects occasional rule violations at controlled rates for testing.
    All outputs are explicitly watermarked with 'mock'.
    """

    def __init__(self, model: str = "mock-model-v1", violation_rate: float = 0.1, seed: int = 42) -> None:
        self.model = f"mock/{model}"
        self.violation_rate = violation_rate
        self.rng = random.Random(seed)

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 150,
    ) -> CompletionResult:
        # Check if task is JSON decision or announcement
        is_decision = "schema" in (system_prompt or "") or "decision" in prompt.lower()

        if is_decision:
            # Return valid JSON
            if self.rng.random() < self.violation_rate:
                # Injected JSON malformation
                text = "{speak: true, level: 2}"
            else:
                text = '{"speak": true, "event": "escalate", "level": 2}'
            return CompletionResult(
                text=text,
                model=self.model,
                latency_s=0.25,
                input_tokens=120,
                output_tokens=25,
            )

        # Announcement task
        is_hindi = "hindi" in prompt.lower() or "Target Language: hi" in prompt

        if self.rng.random() < self.violation_rate:
            # Injected rule violation: indoor ventilation word
            if is_hindi:
                text = "खिड़कियां खोलें और ताजी हवा आने दें।"
            else:
                text = "Please open the windows and ventilate the room."
        else:
            if is_hindi:
                text = "वायु गुणवत्ता खराब है। कृपया खेलकूद की गतिविधियाँ भीतर आयोजित करें।"
            else:
                text = "Air quality is poor. Please reduce outdoor physical activities and play indoors."

        return CompletionResult(
            text=text,
            model=self.model,
            latency_s=0.35,
            input_tokens=95,
            output_tokens=22,
        )
