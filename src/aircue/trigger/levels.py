"""Alert level definitions, thresholds, and hysteresis logic."""
from __future__ import annotations

from typing import Dict, NamedTuple


class LevelSpec(NamedTuple):
    level: int
    name: str
    enter_aqi: float
    exit_aqi: float
    reminder_seconds: float


# Default CPCB-aligned operational bands
DEFAULT_LEVELS: Dict[int, LevelSpec] = {
    0: LevelSpec(0, "Normal", 0.0, 0.0, 0.0),
    1: LevelSpec(1, "Moderate", 101.0, 90.0, 10800.0),   # 180 min
    2: LevelSpec(2, "Poor", 201.0, 185.0, 7200.0),       # 120 min
    3: LevelSpec(3, "Very Poor", 301.0, 280.0, 3600.0),  # 60 min
    4: LevelSpec(4, "Severe", 401.0, 375.0, 1800.0),     # 30 min
}


def determine_level_for_aqi(
    aqi: float,
    current_level: int,
    levels: Dict[int, LevelSpec] = DEFAULT_LEVELS,
) -> int:
    """Determine target alert level applying hysteresis based on current level.

    - Escalation: enters a higher level if aqi >= enter_aqi of that higher level.
    - De-escalation: drops back to a lower level only when aqi < exit_aqi of current level.
    """
    if aqi < 0.0:
        return current_level

    # Check for escalation to higher levels (evaluated top-down)
    for lvl in sorted(levels.keys(), reverse=True):
        if lvl > current_level and aqi >= levels[lvl].enter_aqi:
            return lvl

    # Check for de-escalation: can current level still be sustained?
    if current_level > 0:
        spec = levels[current_level]
        if aqi < spec.exit_aqi:
            # Drop down iteratively until finding the level whose exit threshold is satisfied
            target = current_level - 1
            while target > 0 and aqi < levels[target].exit_aqi:
                target -= 1
            return max(0, target)

    return current_level
