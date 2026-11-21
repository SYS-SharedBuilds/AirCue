"""Robust output parsing and reasoning token stripper."""
from __future__ import annotations

import json
import re
from typing import Any


def strip_reasoning_artifacts(text: str) -> str:
    """Strip <think>...</think> chain-of-thought tags, markdown fences, and outer quotation marks."""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Clean markdown code blocks
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE)
    cleaned = cleaned.strip()
    # Strip wrapping outer double or single quotes if present
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
        cleaned = cleaned[1:-1].strip()
    return cleaned


def parse_json_robust(text: str) -> dict[str, Any] | None:
    """Attempt robust extraction and parsing of JSON dictionary from LLM response text."""
    cleaned = strip_reasoning_artifacts(text)

    # First attempt direct parse
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # Second attempt: extract outermost curly braces
    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    return None
