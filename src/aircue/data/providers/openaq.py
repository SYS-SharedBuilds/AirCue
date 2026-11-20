"""OpenAQ v3 client for ground station observations and MP locality monitoring."""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger("aircue.data.openaq")

OPENAQ_BASE_URL = "https://api.openaq.org/v3"


def get_default_catalog_path() -> Path:
    """Return path to cached MP stations catalog."""
    return Path(__file__).resolve().parents[4] / "data" / "openaq_mp_stations_catalog.json"


def fetch_sensor_hours(
    sensor_id: int,
    client: httpx.Client,
    headers: dict[str, str],
    limit: int = 1000,
    max_pages: int = 3,
) -> dict[str, float]:
    """Fetch hourly values for a sensor mapping timestamp (ISO string) -> value."""
    result: dict[str, float] = {}
    for page in range(1, max_pages + 1):
        try:
            resp = client.get(
                f"{OPENAQ_BASE_URL}/sensors/{sensor_id}/hours",
                params={"limit": limit, "page": page},
                headers=headers,
            )
            if resp.status_code != 200:
                logger.warning(f"Error fetching sensor {sensor_id} page {page}: {resp.status_code}")
                break
            items = resp.json().get("results", [])
            if not items:
                break
            for it in items:
                period = it.get("period", {})
                dt_to = period.get("datetimeTo", {})
                ts = dt_to.get("local") or dt_to.get("utc")
                val = it.get("value")
                if ts and val is not None and val >= 0:
                    result[ts] = float(val)
            if len(items) < limit:
                break
            time.sleep(0.15)
        except Exception as e:
            logger.warning(f"Exception fetching sensor {sensor_id} page {page}: {e}")
            break
    return result


def fetch_openaq_locality_data(
    station_meta: dict[str, Any],
    api_key: str | None = None,
    client: httpx.Client | None = None,
) -> list[dict[str, Any]]:
    """Fetch physical sensor readings from OpenAQ v3 for a single station."""
    key = api_key or os.environ.get("OPENAQ_API_KEY")
    if not key:
        return []

    headers = {"X-API-Key": key, "User-Agent": "AirCue/0.1.0"}
    station_id = station_meta.get("id")
    station_name = station_meta.get("name", f"Station-{station_id}")
    lat = station_meta.get("latitude")
    lon = station_meta.get("longitude")
    pm25_s = station_meta.get("pm25_sensor")
    pm10_s = station_meta.get("pm10_sensor")

    should_close = False
    if client is None:
        client = httpx.Client(timeout=15.0)
        should_close = True

    rows: list[dict[str, Any]] = []
    try:
        pm25_map: dict[str, float] = {}
        pm10_map: dict[str, float] = {}

        if pm25_s:
            pm25_map = fetch_sensor_hours(pm25_s, client, headers)
        if pm10_s:
            pm10_map = fetch_sensor_hours(pm10_s, client, headers)

        all_timestamps = sorted(set(pm25_map.keys()).union(set(pm10_map.keys())))

        for ts in all_timestamps:
            p25 = pm25_map.get(ts)
            p10 = pm10_map.get(ts)

            # Synthesize approximate pair if only one particulate channel is present
            if p25 is None and p10 is not None:
                p25 = round(p10 * 0.55, 1)
            elif p10 is None and p25 is not None:
                p10 = round(p25 * 1.6, 1)

            if p25 is None or p10 is None:
                continue

            rows.append({
                "timestamp": ts,
                "location": station_name,
                "latitude": lat,
                "longitude": lon,
                "pm2_5": p25,
                "pm10": p10,
                "temperature_2m": None,
                "relative_humidity_2m": None,
                "provider": "openaq_cpcb",
                "dataset_kind": "measured_station",
            })
    finally:
        if should_close:
            client.close()

    return rows


def fetch_all_mp_openaq_stations(
    catalog_path: str | Path | None = None,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch all physical MP ground station locality data using cached catalog."""
    key = api_key or os.environ.get("OPENAQ_API_KEY")
    if not key:
        logger.warning("No OPENAQ_API_KEY provided; skipping OpenAQ ground station fetch.")
        return []

    cat_path = Path(catalog_path) if catalog_path else get_default_catalog_path()
    if not cat_path.exists():
        logger.error(f"Catalog file not found at {cat_path}")
        return []

    with open(cat_path, encoding="utf-8") as f:
        catalog = json.load(f)

    all_rows: list[dict[str, Any]] = []
    with httpx.Client(timeout=20.0) as client:
        for sid, meta in catalog.items():
            name = meta.get("name", f"Station-{sid}")
            logger.info(f"Fetching OpenAQ physical locality data for {name} (ID: {sid})...")
            rows = fetch_openaq_locality_data(meta, api_key=key, client=client)
            all_rows.extend(rows)
            time.sleep(0.2)

    return all_rows
