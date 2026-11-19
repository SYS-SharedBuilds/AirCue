"""Deterministic, side-effect-free outdoor AQI trigger state machine.

Time is strictly injected to guarantee determinism in tests and replays.
No network, I/O, or LLM dependencies exist within this module.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple

from aircue.trigger.levels import DEFAULT_LEVELS, LevelSpec, determine_level_for_aqi

EventKind = Literal["escalate", "reminder", "improving", "recovered"]


@dataclass(frozen=True)
class Event:
    """Immutable event emitted when speech announcement is warranted."""
    kind: EventKind
    level: int
    timestamp: float
    aqi: float
    previous_level: int = 0


class AQIMonitor:
    """Stateful, side-effect-free AQI event detector."""

    def __init__(
        self,
        confirm_seconds: float = 3600.0,
        min_confirm_samples: int = 2,
        max_gap_seconds: float = 10800.0,
        levels: Optional[Dict[int, LevelSpec]] = None,
    ) -> None:
        self.confirm_seconds = confirm_seconds
        self.min_confirm_samples = min_confirm_samples
        self.max_gap_seconds = max_gap_seconds
        self.levels = levels or DEFAULT_LEVELS

        # Internal state
        self.current_level: int = 0
        self.last_spoken_time: Optional[float] = None
        self.last_valid_time: Optional[float] = None
        self.last_valid_aqi: Optional[float] = None

        # Sustained escalation tracking: buffer of (timestamp, aqi, tentative_level)
        self._pending_samples: List[Tuple[float, float, int]] = []
        self._is_stale: bool = False

    @property
    def is_stale(self) -> bool:
        """True if time since last valid reading exceeded max_gap_seconds."""
        return self._is_stale

    def update(self, aqi: Optional[float], now: float) -> Optional[Event]:
        """Update monitor with a new AQI reading at time `now` (in seconds).

        Returns an Event if an announcement is warranted, or None otherwise.
        """
        # Validate data hygiene: discard None, NaN, inf, or negative
        if aqi is None or math.isnan(aqi) or math.isinf(aqi) or aqi < 0.0:
            if self.last_valid_time is not None and (now - self.last_valid_time) > self.max_gap_seconds:
                self._is_stale = True
                self._pending_samples.clear()
            return None

        # Check gap since previous valid sample
        if self.last_valid_time is not None and (now - self.last_valid_time) > self.max_gap_seconds:
            # Data gap was exceeded: reset pending escalation state and flag stale
            self._is_stale = True
            self._pending_samples.clear()
        else:
            self._is_stale = False

        self.last_valid_time = now
        self.last_valid_aqi = aqi

        # Evaluate what level this raw AQI points to relative to current level
        target_level = determine_level_for_aqi(aqi, self.current_level, self.levels)

        # Case 1: Escalation (target_level > current_level)
        if target_level > self.current_level:
            # Add to pending buffer
            self._pending_samples.append((now, aqi, target_level))

            # Escalation requires sustained samples spanning confirm_seconds
            if len(self._pending_samples) >= self.min_confirm_samples:
                earliest_ts = self._pending_samples[0][0]
                span = now - earliest_ts
                # Verify that all spanning samples support at least this target_level
                min_pending_lvl = min(s[2] for s in self._pending_samples)

                if span >= self.confirm_seconds and min_pending_lvl > self.current_level:
                    prev = self.current_level
                    self.current_level = min_pending_lvl
                    self.last_spoken_time = now
                    self._pending_samples.clear()
                    return Event(
                        kind="escalate",
                        level=self.current_level,
                        timestamp=now,
                        aqi=aqi,
                        previous_level=prev,
                    )
            return None

        # Clear pending escalation buffer if target_level is not above current_level
        self._pending_samples.clear()

        # Case 2: De-escalation (target_level < current_level)
        if target_level < self.current_level:
            prev = self.current_level
            self.current_level = target_level
            self.last_spoken_time = now

            if self.current_level == 0:
                return Event(
                    kind="recovered",
                    level=0,
                    timestamp=now,
                    aqi=aqi,
                    previous_level=prev,
                )
            else:
                return Event(
                    kind="improving",
                    level=self.current_level,
                    timestamp=now,
                    aqi=aqi,
                    previous_level=prev,
                )

        # Case 3: Reminder while steady at level > 0
        if self.current_level > 0 and self.last_spoken_time is not None:
            spec = self.levels.get(self.current_level)
            if spec and spec.reminder_seconds > 0:
                elapsed = now - self.last_spoken_time
                if elapsed >= spec.reminder_seconds:
                    self.last_spoken_time = now
                    return Event(
                        kind="reminder",
                        level=self.current_level,
                        timestamp=now,
                        aqi=aqi,
                        previous_level=self.current_level,
                    )

        return None
