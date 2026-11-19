"""Pre-rendered audio clip generation and manifest management."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aircue.audio.tts import synthesize_speech
from aircue.messages.builder import build_message
from aircue.trigger.engine import Event


def build_all_clips(
    output_dir: str | Path = "clips",
    backend: str = "beep",
    force: bool = False,
) -> dict[str, Any]:
    """Pregenerate audio clips for all template variants and write manifest.json."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"

    manifest: dict[str, Any] = {}
    if manifest_path.exists() and not force:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    languages = ["en", "hi"]
    tones = ["neutral", "young"]
    slots = [None, "assembly", "sports_pt", "recess", "dismissal"]

    events = [
        Event(kind="escalate", level=1, timestamp=0.0, aqi=150.0),
        Event(kind="escalate", level=2, timestamp=0.0, aqi=250.0),
        Event(kind="escalate", level=3, timestamp=0.0, aqi=350.0),
        Event(kind="escalate", level=4, timestamp=0.0, aqi=450.0),
        Event(kind="reminder", level=1, timestamp=0.0, aqi=150.0),
        Event(kind="reminder", level=2, timestamp=0.0, aqi=250.0),
        Event(kind="reminder", level=3, timestamp=0.0, aqi=350.0),
        Event(kind="reminder", level=4, timestamp=0.0, aqi=450.0),
        Event(kind="improving", level=1, timestamp=0.0, aqi=150.0),
        Event(kind="recovered", level=0, timestamp=0.0, aqi=40.0),
    ]

    total_created = 0
    clips_info: dict[str, Any] = manifest.get("clips", {})

    for ev in events:
        for lang in languages:
            for tone in tones:
                for slot in slots:
                    msg = build_message(ev, language=lang, tone=tone, slot=slot)
                    clip_file = f"{msg.clip_id}.wav"
                    clip_path = out_dir / clip_file

                    if not clip_path.exists() or force:
                        synthesize_speech(
                            text=msg.text,
                            language=lang,
                            output_path=clip_path,
                            backend=backend,
                        )
                        total_created += 1

                    clips_info[msg.clip_id] = {
                        "text": msg.text,
                        "language": lang,
                        "tone": tone,
                        "slot": slot,
                        "event_key": msg.event_key,
                        "file": clip_file,
                    }

    manifest["backend"] = backend
    manifest["total_clips"] = len(clips_info)
    manifest["clips"] = clips_info

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest
