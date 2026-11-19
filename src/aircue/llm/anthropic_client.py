"""Anthropic Messages API client (ready for future activation via config)."""
from __future__ import annotations

import os
import time
from typing import Optional
import httpx

from aircue.llm.base import CompletionResult, LLMClient


class AnthropicClient(LLMClient):
    """Anthropic Messages API client."""

    def __init__(
        self,
        model: str = "claude-haiku-5-5",
        api_key_env: str = "ANTHROPIC_API_KEY",
        timeout_seconds: float = 30.0,
    ) -> None:
        self.model = model
        self.api_key = os.environ.get(api_key_env, "")
        self.timeout_seconds = timeout_seconds

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 150,
    ) -> CompletionResult:
        if not self.api_key:
            return CompletionResult(
                text="",
                model=self.model,
                latency_s=0.0,
                raw_error="Missing ANTHROPIC_API_KEY environment variable",
            )

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        start_t = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                resp = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
                latency = time.perf_counter() - start_t
                if resp.status_code != 200:
                    return CompletionResult(text="", model=self.model, latency_s=latency, raw_error=resp.text)

                data = resp.json()
                content_blocks = data.get("content", [])
                text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
                usage = data.get("usage", {})
                return CompletionResult(
                    text=text.strip(),
                    model=self.model,
                    latency_s=latency,
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                )
            except Exception as e:
                return CompletionResult(text="", model=self.model, latency_s=time.perf_counter() - start_t, raw_error=str(e))
