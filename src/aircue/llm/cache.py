"""On-disk deterministic caching for validated LLM announcements."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class WordingCache:
    """File-backed cache keyed by model, prompt version, facts, language, and tone."""

    def __init__(self, cache_file: str | Path = "results/wording_cache.json") -> None:
        self.cache_path = Path(cache_file)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}

    def _save(self) -> None:
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _make_key(self, model: str, prompt_version: str, facts: dict[str, Any], lang: str, tone: str) -> str:
        serialized = json.dumps(facts, sort_keys=True)
        raw = f"{model}:{prompt_version}:{lang}:{tone}:{serialized}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, model: str, prompt_version: str, facts: dict[str, Any], lang: str, tone: str) -> str | None:
        key = self._make_key(model, prompt_version, facts, lang, tone)
        return self._cache.get(key)

    def set(self, model: str, prompt_version: str, facts: dict[str, Any], lang: str, tone: str, text: str) -> None:
        key = self._make_key(model, prompt_version, facts, lang, tone)
        self._cache[key] = text
        self._save()
