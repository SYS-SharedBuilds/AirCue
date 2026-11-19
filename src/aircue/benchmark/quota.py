"""Persistent daily request quota manager for OpenRouter free-tier runs."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class QuotaManager:
    """Tracks daily API calls against configured limits, enabling multi-day resumable benchmarks."""

    def __init__(self, state_file: str | Path = "results/quota.json", daily_budget: int = 180) -> None:
        self.state_path = Path(state_file)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.daily_budget = daily_budget
        self._state: dict[str, Any] = {}
        self._load()

    def _today_key(self) -> str:
        return datetime.now(UTC).strftime("%Y-%m-%d")

    def _load(self) -> None:
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    self._state = json.load(f)
            except Exception:
                self._state = {}

    def _save(self) -> None:
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2)
        except Exception:
            pass

    def get_calls_today(self) -> int:
        today = self._today_key()
        return self._state.get(today, {}).get("calls", 0)

    def can_call(self) -> bool:
        return self.get_calls_today() < self.daily_budget

    def record_call(self, tokens: int = 0) -> None:
        today = self._today_key()
        curr = self._state.setdefault(today, {"calls": 0, "total_tokens": 0})
        curr["calls"] += 1
        curr["total_tokens"] += tokens
        self._save()

    def remaining_today(self) -> int:
        return max(0, self.daily_budget - self.get_calls_today())
