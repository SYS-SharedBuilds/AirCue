"""Sunlight-readable LED color mapping and MQTT publisher."""
from __future__ import annotations

from typing import NamedTuple


class LEDState(NamedTuple):
    color: str
    pattern: str  # 'solid' or 'blink'
    hex_rgb: str


# Mappings for outdoor sunlight LED array:
# Level 0 (Normal): Green solid
# Level 1 (Moderate): Yellow solid
# Level 2 (Poor): Orange / Yellow blinking
# Level 3 (Very Poor): Red solid
# Level 4 (Severe): Red blinking
LED_LEVEL_MAP: dict[int, LEDState] = {
    0: LEDState("green", "solid", "#00FF00"),
    1: LEDState("yellow", "solid", "#FFFF00"),
    2: LEDState("orange", "blink", "#FFA500"),
    3: LEDState("red", "solid", "#FF0000"),
    4: LEDState("red", "blink", "#FF0000"),
}


def get_led_state(level: int) -> LEDState:
    """Retrieve LED color pattern for given AQI level (0 to 4)."""
    clamped = max(0, min(4, level))
    return LED_LEVEL_MAP[clamped]
