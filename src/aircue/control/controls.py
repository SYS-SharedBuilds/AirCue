"""System runtime controls: mute, snooze, acknowledge, and exam mode."""
from __future__ import annotations

import time
from typing import Optional


class SystemControls:
    """Tracks physical button overrides and administrative control states."""

    def __init__(self, default_snooze_seconds: float = 1800.0) -> None:
        self.default_snooze_seconds = default_snooze_seconds
        self.is_muted: bool = False
        self.is_exam_mode: bool = False
        self._snooze_until: Optional[float] = None

    def toggle_mute(self) -> bool:
        """Toggle mute state. When muted, LED updates continue but speech is silenced."""
        self.is_muted = not self.is_muted
        return self.is_muted

    def set_exam_mode(self, enabled: bool) -> None:
        """In exam mode, system runs strictly visual LED indicators, silencing speaker."""
        self.is_exam_mode = enabled

    def snooze(self, seconds: Optional[float] = None) -> float:
        """Snooze voice alerts for duration (default 30 min / 1800s)."""
        duration = seconds if seconds is not None else self.default_snooze_seconds
        self._snooze_until = time.time() + duration
        return self._snooze_until

    def is_speech_suppressed(self, now: Optional[float] = None) -> tuple[bool, Optional[str]]:
        """Check if speech output is currently suppressed.

        Returns (suppressed: bool, reason: str | None).
        """
        curr = now if now is not None else time.time()

        if self.is_exam_mode:
            return True, "exam_mode"
        if self.is_muted:
            return True, "muted"
        if self._snooze_until is not None:
            if curr < self._snooze_until:
                return True, "snoozed"
            else:
                self._snooze_until = None  # Expired

        return False, None
