"""Comprehensive integration test suite verifying full system pipeline offline."""
from pathlib import Path

import pytest

from aircue.benchmark.runner import run_benchmark_suite
from aircue.config import load_config
from aircue.data.store import load_latest_snapshot
from aircue.llm.validators import validate_announcement
from aircue.messages.builder import build_message
from aircue.replay.replay import run_historical_replay
from aircue.trigger.engine import AQIMonitor


def test_full_offline_pipeline():
    # 1. Config loading
    cfg = load_config()
    assert cfg.site.id == "indore_school_01"

    # 2. Dataset snapshot
    df = load_latest_snapshot()
    assert len(df) > 1000
    assert "Indore" in df["location"].values

    # 3. Trigger state machine
    monitor = AQIMonitor(confirm_seconds=600.0, min_confirm_samples=2)
    ev1 = monitor.update(45.0, now=0.0)
    assert ev1 is None

    monitor.update(250.0, now=100.0)
    ev_esc = monitor.update(250.0, now=701.0)
    assert ev_esc is not None
    assert ev_esc.kind == "escalate"
    assert ev_esc.level == 2

    # 4. Message generation
    msg_en = build_message(ev_esc, language="en", slot="sports_pt")
    assert "indoor" in msg_en.text.lower() or "play" in msg_en.text.lower()
    assert "window" not in msg_en.text.lower()
    # Ensure physical doors are not mentioned as ventilation actions
    import re
    assert not re.search(r"\bdoor[s]?\b", msg_en.text.lower())

    msg_hi = build_message(ev_esc, language="hi")
    assert "खराब" in msg_hi.text
    assert "खिड़की" not in msg_hi.text

    # 5. Safety validation
    facts = {"level": 2, "category": "Poor", "aqi": 250, "pm25": 85.0, "site": "Indore"}
    val = validate_announcement(msg_en.text, expected_lang="en", input_facts=facts)
    assert val.passed is True

    # 6. Historical replay integration
    snapshot_path = sorted(Path("data/snapshots").glob("aqi_snapshot_*.csv"))[-1]
    rep = run_historical_replay(snapshot_path, location="Indore")
    assert rep["total_events"] > 0


@pytest.mark.asyncio
async def test_mock_benchmark_pipeline(tmp_path):
    log_file = tmp_path / "test_benchmark.jsonl"
    results = await run_benchmark_suite(use_mock=True, limit=2, raw_log_path=log_file)
    assert len(results) == 8  # 2 models * (2 generation + 2 decision)
    assert log_file.exists()
