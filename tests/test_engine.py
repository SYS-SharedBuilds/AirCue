"""Unit tests and hypothesis property tests for AQIMonitor state machine."""
import pytest
from hypothesis import given, strategies as st
from aircue.trigger.engine import AQIMonitor, Event
from aircue.trigger.levels import determine_level_for_aqi


def test_escalation_confirmation_delay():
    # 3600s confirmation, min 2 samples
    monitor = AQIMonitor(confirm_seconds=3600.0, min_confirm_samples=2)

    # Initial normal reading
    ev = monitor.update(aqi=50.0, now=0.0)
    assert ev is None
    assert monitor.current_level == 0

    # AQI jumps to Poor (250) at t=100s
    ev = monitor.update(aqi=250.0, now=100.0)
    assert ev is None  # Not confirmed yet
    assert monitor.current_level == 0

    # Intermediate sample at t=1800s (below confirm_seconds)
    ev = monitor.update(aqi=260.0, now=1800.0)
    assert ev is None
    assert monitor.current_level == 0

    # Sample at t=3701s spanning > 3600s
    ev = monitor.update(aqi=255.0, now=3701.0)
    assert ev is not None
    assert ev.kind == "escalate"
    assert ev.level == 2
    assert monitor.current_level == 2


def test_single_spike_ignored():
    monitor = AQIMonitor(confirm_seconds=3600.0, min_confirm_samples=2)

    monitor.update(aqi=45.0, now=0.0)
    # Huge spike for 1 sample
    monitor.update(aqi=450.0, now=1000.0)
    assert monitor.current_level == 0

    # Drops back to normal
    monitor.update(aqi=45.0, now=2000.0)
    assert monitor.current_level == 0

    # Later normal sample after confirm window
    ev = monitor.update(aqi=45.0, now=4000.0)
    assert ev is None
    assert monitor.current_level == 0


def test_hysteresis_and_multi_level_recovery():
    monitor = AQIMonitor(confirm_seconds=600.0, min_confirm_samples=2)

    # Escalate to Level 3 (Very Poor: 350)
    monitor.update(350.0, now=0.0)
    ev = monitor.update(350.0, now=601.0)
    assert ev is not None
    assert ev.level == 3
    assert monitor.current_level == 3

    # Drops to 290 (below exit threshold 280? No, 290 >= 280, so stays at 3)
    ev = monitor.update(290.0, now=700.0)
    assert ev is None
    assert monitor.current_level == 3

    # Drops to 270 (below 280 exit threshold, but >= 185 exit for level 2)
    ev = monitor.update(270.0, now=800.0)
    assert ev is not None
    assert ev.kind == "improving"
    assert ev.level == 2
    assert monitor.current_level == 2

    # Sudden clean air drop to 40 (drops past 1 to 0)
    ev = monitor.update(40.0, now=900.0)
    assert ev is not None
    assert ev.kind == "recovered"
    assert ev.level == 0
    assert monitor.current_level == 0


def test_reminders_cadence():
    # Level 2 reminder interval is 7200s (120 min)
    monitor = AQIMonitor(confirm_seconds=600.0, min_confirm_samples=2)

    monitor.update(250.0, now=0.0)
    ev = monitor.update(250.0, now=601.0)
    assert ev is not None
    assert ev.kind == "escalate"

    # Before reminder interval
    assert monitor.update(250.0, now=601.0 + 3600.0) is None

    # At or after reminder interval
    ev_rem = monitor.update(250.0, now=601.0 + 7201.0)
    assert ev_rem is not None
    assert ev_rem.kind == "reminder"
    assert ev_rem.level == 2


def test_stale_data_gap_clears_pending():
    monitor = AQIMonitor(confirm_seconds=3600.0, min_confirm_samples=2, max_gap_seconds=10800.0)

    monitor.update(250.0, now=0.0)
    # Gap of 12000s (> 10800 max_gap_seconds)
    monitor.update(None, now=12000.0)
    assert monitor.is_stale is True

    # Next reading arrives: should not trigger an escalation based on old sample
    ev = monitor.update(250.0, now=12001.0)
    assert ev is None
    assert monitor.current_level == 0


@given(st.floats(min_value=0.0, max_value=600.0), st.integers(min_value=0, max_value=4))
def test_determine_level_bounds(aqi, current_level):
    lvl = determine_level_for_aqi(aqi, current_level)
    assert 0 <= lvl <= 4
