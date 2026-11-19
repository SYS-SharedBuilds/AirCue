"""Telemetry data sources: ApiPollSource, CsvReplaySource, and MqttSource."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Iterator, Optional
import pandas as pd

from aircue.data.providers.open_meteo import fetch_open_meteo_city


class TelemetryReading:
    """Normalized telemetry reading record."""

    def __init__(
        self,
        timestamp: float,
        pm2_5: Optional[float] = None,
        pm10: Optional[float] = None,
        temperature: Optional[float] = None,
        humidity: Optional[float] = None,
        aqi: Optional[float] = None,
        site: str = "default",
    ) -> None:
        self.timestamp = timestamp
        self.pm2_5 = pm2_5
        self.pm10 = pm10
        self.temperature = temperature
        self.humidity = humidity
        self.aqi = aqi
        self.site = site


class BaseTelemetrySource(ABC):
    """Abstract interface for sensor data streams."""

    @abstractmethod
    def start(self, callback: Callable[[TelemetryReading], None]) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass


class CsvReplaySource(BaseTelemetrySource):
    """Replays historical CSV snapshots at configurable speed."""

    def __init__(self, csv_path: str, location: str = "Indore", speed: float = 1.0) -> None:
        self.csv_path = csv_path
        self.location = location
        self.speed = speed
        self._running = False

    def stream(self) -> Iterator[TelemetryReading]:
        df = pd.read_csv(self.csv_path)
        if "location" in df.columns:
            df = df[df["location"].str.lower() == self.location.lower()]

        df["dt"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(by="dt")

        prev_time = None
        for _, row in df.iterrows():
            ts = row["dt"].timestamp()
            if prev_time is not None and self.speed > 0:
                delta = (ts - prev_time) / self.speed
                # Limit maximum sleep during fast replay
                if delta > 0:
                    time.sleep(min(0.1, delta))
            prev_time = ts

            yield TelemetryReading(
                timestamp=ts,
                pm2_5=row.get("pm2_5"),
                pm10=row.get("pm10"),
                aqi=row.get("cpcb_aqi"),
                site=self.location,
            )

    def start(self, callback: Callable[[TelemetryReading], None]) -> None:
        self._running = True
        for reading in self.stream():
            if not self._running:
                break
            callback(reading)

    def stop(self) -> None:
        self._running = False


class ApiPollSource(BaseTelemetrySource):
    """Virtual sensor: periodically queries live API for location readings."""

    def __init__(self, lat: float, lon: float, location: str, interval_seconds: float = 300.0) -> None:
        self.lat = lat
        self.lon = lon
        self.location = location
        self.interval = interval_seconds
        self._running = False

    def start(self, callback: Callable[[TelemetryReading], None]) -> None:
        self._running = True
        while self._running:
            try:
                rows = fetch_open_meteo_city(self.lat, self.lon, self.location, past_days=1)
                if rows:
                    latest = rows[-1]
                    reading = TelemetryReading(
                        timestamp=time.time(),
                        pm2_5=latest.get("pm2_5"),
                        pm10=latest.get("pm10"),
                        aqi=latest.get("cpcb_aqi"),
                        site=self.location,
                    )
                    callback(reading)
            except Exception:
                pass
            time.sleep(self.interval)

    def stop(self) -> None:
        self._running = False
