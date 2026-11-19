"""AirCue system configuration loader and models."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class OutdoorSlot(BaseModel):
    start: str
    end: str
    name: str


class ScheduleConfig(BaseModel):
    school_days: list[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5])
    start_time: str = "08:00"
    end_time: str = "15:00"
    holidays: list[str] = Field(default_factory=list)
    outdoor_slots: dict[str, OutdoorSlot] = Field(default_factory=dict)


class LevelConfig(BaseModel):
    name: str
    enter_aqi: int
    exit_aqi: int
    reminder_seconds: int = 0


class HumidityCorrectionConfig(BaseModel):
    enabled: bool = False
    factor: float = 0.25
    rh_threshold: float = 65.0


class TriggerConfig(BaseModel):
    aqi_source: str = "cpcb_computed"
    profile: str = "api_hourly"
    confirm_seconds: int = 3600
    min_confirm_samples: int = 2
    max_gap_seconds: int = 10800
    levels: dict[int, LevelConfig] = Field(default_factory=dict)
    humidity_correction: HumidityCorrectionConfig = Field(default_factory=HumidityCorrectionConfig)


class MessagesConfig(BaseModel):
    default_language: str = "en"
    default_tone: str = "neutral"
    allow_masks_recommendation: bool = False


class AudioConfig(BaseModel):
    backend: str = "beep"
    clips_dir: str = "clips"
    volume_gain: float = 1.0


class MqttConfig(BaseModel):
    broker: str = "localhost"
    port: int = 1883
    keepalive: int = 60
    topics: dict[str, str] = Field(default_factory=dict)


class SiteConfig(BaseModel):
    id: str = "indore_school_01"
    name: str = "PIEMR Campus Grounds, Indore"
    timezone: str = "Asia/Kolkata"


class AirCueConfig(BaseModel):
    site: SiteConfig = Field(default_factory=SiteConfig)
    trigger: TriggerConfig = Field(default_factory=TriggerConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    messages: MessagesConfig = Field(default_factory=MessagesConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    mqtt: MqttConfig = Field(default_factory=MqttConfig)


def load_config(config_path: str | Path | None = None) -> AirCueConfig:
    """Load configuration from a YAML file, falling back to configs/aircue.yaml."""
    if config_path is None:
        config_path = Path("configs/aircue.yaml")
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        return AirCueConfig()

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return AirCueConfig.model_validate(data)


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Helper to safely read an arbitrary YAML file."""
    p = Path(path)
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
