"""AirCue Runtime Orchestration Service.

Wires telemetry source -> trigger engine -> message builder -> audio player.
Maintains decision logging into results/announcements.jsonl.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from aircue.audio.player import AudioPlayer, NullPlayer
from aircue.config import AirCueConfig
from aircue.control.controls import SystemControls
from aircue.control.leds import get_led_state
from aircue.control.schedule import SchoolSchedule
from aircue.messages.builder import build_message
from aircue.transport.mqtt import MqttClient
from aircue.transport.sources import BaseTelemetrySource, TelemetryReading
from aircue.trigger.aqi import calculate_cpcb_aqi
from aircue.trigger.engine import AQIMonitor, Event
from aircue.trigger.humidity import correct_pm_for_humidity
from aircue.trigger.levels import LevelSpec


class AirCueService:
    """Core runtime service."""

    def __init__(
        self,
        config: AirCueConfig,
        source: BaseTelemetrySource,
        log_file: str | Path = "results/announcements.jsonl",
        use_null_player: bool = False,
    ) -> None:
        self.config = config
        self.source = source
        self.log_path = Path(log_file)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert config levels to LevelSpec dict
        level_specs: Dict[int, LevelSpec] = {}
        for lvl, c in self.config.trigger.levels.items():
            level_specs[lvl] = LevelSpec(
                level=lvl,
                name=c.name,
                enter_aqi=float(c.enter_aqi),
                exit_aqi=float(c.exit_aqi),
                reminder_seconds=float(c.reminder_seconds),
            )

        self.engine = AQIMonitor(
            confirm_seconds=float(self.config.trigger.confirm_seconds),
            min_confirm_samples=self.config.trigger.min_confirm_samples,
            max_gap_seconds=float(self.config.trigger.max_gap_seconds),
            levels=level_specs if level_specs else None,
        )

        self.schedule = SchoolSchedule(self.config.schedule, timezone=self.config.site.timezone)
        self.controls = SystemControls()
        self.player = NullPlayer() if use_null_player else AudioPlayer()
        self.mqtt_client = MqttClient(broker=self.config.mqtt.broker, port=self.config.mqtt.port)
        self.site_id = self.config.site.id

    def handle_telemetry(self, reading: TelemetryReading) -> Optional[Event]:
        """Process an incoming telemetry reading through full pipeline."""
        now_ts = reading.timestamp
        dt = datetime.fromtimestamp(now_ts, tz=timezone.utc)

        # 1. Apply humidity correction if enabled
        pm25 = reading.pm2_5
        if self.config.trigger.humidity_correction.enabled and reading.humidity is not None:
            pm25 = correct_pm_for_humidity(
                pm25,
                reading.humidity,
                factor=self.config.trigger.humidity_correction.factor,
                rh_threshold=self.config.trigger.humidity_correction.rh_threshold,
            )

        # 2. Derive AQI
        aqi = reading.aqi
        if aqi is None and pm25 is not None:
            aqi = calculate_cpcb_aqi(pm25, reading.pm10)

        # 3. Update state machine
        event = self.engine.update(aqi, now=now_ts)

        # 4. Update LEDs regardless of speech suppression
        current_lvl = self.engine.current_level
        led = get_led_state(current_lvl)
        self.mqtt_client.publish(
            f"aircue/{self.site_id}/led",
            {"level": current_lvl, "color": led.color, "pattern": led.pattern, "hex": led.hex_rgb},
        )

        # 5. Check operational gating (schedule & controls)
        suppressed, reason = False, None
        if not self.schedule.is_school_hours(dt):
            suppressed, reason = True, "outside_school_hours"
        else:
            ctrl_suppressed, ctrl_reason = self.controls.is_speech_suppressed(now_ts)
            if ctrl_suppressed:
                suppressed, reason = True, ctrl_reason

        # 6. If event occurred, process announcement
        if event is not None:
            slot = self.schedule.get_current_slot(dt)
            msg = build_message(
                event,
                language=self.config.messages.default_language,
                tone=self.config.messages.default_tone,
                slot=slot,
            )

            spoken = False
            if not suppressed:
                clip_path = Path(self.config.audio.clips_dir) / f"{msg.clip_id}.wav"
                spoken = self.player.play(clip_path)

            # Record announcement decision log
            log_entry = {
                "timestamp": dt.isoformat(),
                "ts_epoch": now_ts,
                "event_kind": event.kind,
                "level": event.level,
                "aqi": event.aqi,
                "spoken": spoken,
                "suppressed": suppressed,
                "suppression_reason": reason,
                "message_text": msg.text,
                "clip_id": msg.clip_id,
                "slot": slot,
            }
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return event

    def run(self) -> None:
        """Connect transport and start processing telemetry stream."""
        self.mqtt_client.connect()
        try:
            self.source.start(self.handle_telemetry)
        finally:
            self.mqtt_client.disconnect()
