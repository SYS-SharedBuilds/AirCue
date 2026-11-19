"""Historical replay and tuning grid tools."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
from rich.console import Console
from rich.table import Table

from aircue.control.service import AirCueService
from aircue.transport.sources import CsvReplaySource
from aircue.config import AirCueConfig


def run_historical_replay(
    csv_path: str | Path,
    location: str = "Indore",
    config: AirCueConfig | None = None,
) -> Dict[str, Any]:
    """Execute trigger engine across historical snapshot and tally metrics."""
    cfg = config or AirCueConfig()
    source = CsvReplaySource(str(csv_path), location=location, speed=0.0)

    # Use null player to suppress actual audio during fast replay
    svc = AirCueService(config=cfg, source=source, use_null_player=True)

    events: List[Any] = []
    def recording_handler(reading: Any) -> None:
        ev = svc.handle_telemetry(reading)
        if ev:
            events.append(ev)

    source.start(recording_handler)

    n_days = 92.0  # Approx snapshot span
    announcements_per_day = len(events) / n_days if n_days > 0 else 0.0

    counts: Dict[str, int] = {}
    for ev in events:
        counts[ev.kind] = counts.get(ev.kind, 0) + 1

    return {
        "location": location,
        "total_events": len(events),
        "announcements_per_day": announcements_per_day,
        "event_counts": counts,
    }
