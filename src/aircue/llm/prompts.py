"""Outdoor prompt templates and versioning."""
from __future__ import annotations

from typing import Any, Optional

PROMPT_VERSION = "2.1.0-outdoor"

SYSTEM_PROMPT_ANNOUNCEMENT = """You are AirCue, an automated outdoor public address voice alert system for a school.
Your task is to generate a short, authoritative, polite spoken announcement for students and teachers outdoors (e.g. at the sports field or assembly area).
Rules you must follow strictly:
1. Output MUST be at most 20 words.
2. Output MUST be 1 or 2 sentences only.
3. Ask for exactly ONE specific outdoor activity action (e.g., move sports indoors, keep assembly brief, pause heavy running).
4. Strictly NO indoor ventilation advice: NEVER mention doors, windows, fresh air exchange, stuffiness, or opening anything.
5. Use only the provided air quality facts; do not invent or add unmentioned numbers or pollutants.
6. Absolutely no scary medical claims, diagnoses, or disease mentions.
7. Return ONLY the spoken text in the requested language, with no preamble, quotes, explanations, or reasoning.
"""

SYSTEM_PROMPT_DECISION = """You are the trigger decision engine for AirCue, an outdoor school air quality voice system.
Given the recent hours of particulate matter (PM2.5, PM10) and AQI readings, decide whether a spoken announcement is warranted right now.
Return strictly a valid JSON object with the following schema:
{
  "speak": boolean,
  "event": "escalate" | "reminder" | "improving" | "recovered" | "none",
  "level": integer (0 to 4)
}
Rules:
- Speak only when air quality warrants an action according to CPCB thresholds (Moderate: 101-200, Poor: 201-300, Very Poor: 301-400, Severe: 401+).
- Single transient spikes should be rejected.
- Return ONLY the JSON object.
"""


def build_announcement_user_prompt(facts: dict[str, Any]) -> str:
    """Format input facts for announcement generation."""
    return f"""Current Outdoor Conditions:
- Level: {facts.get('level')} ({facts.get('category')})
- CPCB AQI: {facts.get('aqi')}
- PM2.5: {facts.get('pm25')} µg/m³
- Location: {facts.get('site')}
- Timetable Slot: {facts.get('activity_slot', 'General')}
- Target Language: {facts.get('language', 'en')} ({'Hindi' if facts.get('language') == 'hi' else 'English'})
- Target Tone: {facts.get('tone', 'neutral')}

Write the spoken announcement now:"""


def build_decision_user_prompt(history_window: list[dict[str, Any]], current_state: Optional[dict[str, Any]] = None) -> str:
    """Format history window for trigger decision evaluation."""
    lines = ["Recent Hourly Outdoor Readings (Oldest to Newest):"]
    for row in history_window:
        lines.append(f"- Time: {row.get('timestamp')}, PM2.5: {row.get('pm2_5')} µg/m³, AQI: {row.get('cpcb_aqi')}")

    if current_state:
        lines.append(f"\nCurrent System State: Level={current_state.get('level')}, Minutes Since Last Alert={current_state.get('minutes_since_last')}")

    lines.append("\nEvaluate the sequence and output the JSON decision:")
    return "\n".join(lines)
