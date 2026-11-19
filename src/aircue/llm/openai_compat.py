"""Generic OpenAI-compatible LLM client (DeepSeek, Moonshot/Kimi)."""
from __future__ import annotations

import os
import time

import httpx

from aircue.llm.base import CompletionResult, LLMClient
from aircue.llm.parsing import strip_reasoning_artifacts


class OpenAICompatClient(LLMClient):
    """Generic client for any OpenAI-compatible completions API."""

    def __init__(
        self,
        model: str,
        base_url: str,
        api_key_env: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get(api_key_env, "")
        self.timeout_seconds = timeout_seconds

    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 150,
    ) -> CompletionResult:
        if not self.api_key:
            return CompletionResult(
                text="",
                model=self.model,
                latency_s=0.0,
                raw_error="API key missing in environment variable",
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        start_t = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                latency = time.perf_counter() - start_t
                if resp.status_code != 200:
                    return CompletionResult(text="", model=self.model, latency_s=latency, raw_error=resp.text)

                data = resp.json()
                choice = data.get("choices", [{}])[0]
                text = strip_reasoning_artifacts(choice.get("message", {}).get("content", ""))
                usage = data.get("usage", {})
                return CompletionResult(
                    text=text,
                    model=self.model,
                    latency_s=latency,
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                )
            except Exception as e:
                return CompletionResult(text="", model=self.model, latency_s=time.perf_counter() - start_t, raw_error=str(e))
