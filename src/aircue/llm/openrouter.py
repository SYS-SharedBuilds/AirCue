"""OpenRouter HTTP client with exponential backoff and quota tracking."""
from __future__ import annotations

import os
import time

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from aircue.llm.base import CompletionResult, LLMClient
from aircue.llm.parsing import strip_reasoning_artifacts


def is_retryable_http_error(exception: BaseException) -> bool:
    """Return True if exception represents a transient 429 or 5xx error without quota exhaustion."""
    if isinstance(exception, httpx.HTTPStatusError):
        status = exception.response.status_code
        if status in (500, 502, 503, 504):
            return True
        if status == 429:
            # Check if this is a rate limit or full daily quota exhaustion
            err_text = exception.response.text.lower()
            if "quota" in err_text or "credits" in err_text or "exhausted" in err_text:
                return False  # Do not retry quota exhaustion
            return True
    return isinstance(exception, (httpx.ConnectError, httpx.TimeoutException))


class OpenRouterClient(LLMClient):
    """OpenRouter OpenAI-compatible chat completion client."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout_seconds: float = 30.0,
        cost_per_m_in: float = 0.0,
        cost_per_m_out: float = 0.0,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.cost_per_m_in = cost_per_m_in
        self.cost_per_m_out = cost_per_m_out

    @retry(
        retry=retry_if_exception(is_retryable_http_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 150,
    ) -> CompletionResult:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.complete_messages(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    @retry(
        retry=retry_if_exception(is_retryable_http_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def complete_messages(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> CompletionResult:
        if not self.api_key:
            return CompletionResult(
                text="",
                model=self.model,
                latency_s=0.0,
                raw_error="Missing OPENROUTER_API_KEY environment variable",
            )

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "reasoning": {"effort": "none"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/yusufmalubhaiwala/AirCue",
            "X-Title": "AirCue Outdoor Voice Alert",
            "Content-Type": "application/json",
        }

        start_t = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            latency = time.perf_counter() - start_t

            if resp.status_code != 200:
                return CompletionResult(
                    text="",
                    model=self.model,
                    latency_s=latency,
                    raw_error=f"HTTP {resp.status_code}: {resp.text}",
                )

            data = resp.json()
            choice = data.get("choices", [{}])[0]
            msg = choice.get("message", {})
            raw_text = msg.get("content", "") or ""
            cleaned_text = strip_reasoning_artifacts(raw_text)

            usage = data.get("usage", {})
            in_tok = usage.get("prompt_tokens", 0)
            out_tok = usage.get("completion_tokens", 0)

            cost = (in_tok / 1_000_000.0) * self.cost_per_m_in + (out_tok / 1_000_000.0) * self.cost_per_m_out

            return CompletionResult(
                text=cleaned_text,
                model=self.model,
                latency_s=latency,
                input_tokens=in_tok,
                output_tokens=out_tok,
                finish_reason=choice.get("finish_reason", "stop"),
                cost_usd=cost,
            )
