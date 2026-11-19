"""AirCue Message Builder: constructs message texts and deterministic clip identifiers."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

from aircue.messages.templates import TEMPLATES_EN, TEMPLATES_HI
from aircue.trigger.engine import Event


@dataclass(frozen=True)
class Message:
    text: str
    language: str
    tone: str
    slot: Optional[str]
    clip_id: str
    event_key: str


def get_event_key(event: Event) -> str:
    """Format event key matching template mapping."""
    if event.kind in ("escalate", "reminder"):
        return f"{event.kind}_{event.level}"
    return event.kind


def build_message(
    event: Event,
    language: str = "en",
    tone: str = "neutral",
    slot: Optional[str] = None,
) -> Message:
    """Assemble a deterministic speech message from templates and return with stable clip ID."""
    lang = "hi" if language.lower() in ("hi", "hindi") else "en"
    templates_dict = TEMPLATES_HI if lang == "hi" else TEMPLATES_EN

    event_key = get_event_key(event)
    template_set = templates_dict.get(event_key, templates_dict["escalate_1"])

    # Determine wording based on timetable slot or tone
    if slot and hasattr(template_set, slot):
        text = getattr(template_set, slot)
    elif tone == "young":
        text = template_set.young
    else:
        text = template_set.neutral

    # Generate stable clip_id
    raw_sig = f"{lang}_{event_key}_{tone}_{slot or 'none'}_{text}"
    content_hash = hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()[:8]
    clip_id = f"{lang}_{event_key}_{content_hash}"

    return Message(
        text=text,
        language=lang,
        tone=tone,
        slot=slot,
        clip_id=clip_id,
        event_key=event_key,
    )
