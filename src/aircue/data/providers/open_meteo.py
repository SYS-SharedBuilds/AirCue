"""Open-Meteo Air Quality API client for historical CAMS atmospheric model data."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from aircue.trigger.aqi import aqi_to_category_cpcb, calculate_cpcb_aqi

OPEN_METEO_AQI_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
HOURLY_VARS = [
    "pm10",
    "pm2_5",
    "us_aqi",
    "european_aqi",
    "ozone",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "carbon_monoxide",
]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_open_meteo_city(
    lat: float,
    lon: float,
    location_name: str,
    past_days: int = 92,
    tz: str = "Asia/Kolkata",
) -> list[dict[str, Any]]:
    """Fetch past hourly air-quality data for a location from Open-Meteo API.

    Enforces data integrity: drops future timestamps (keeps <= now).
    Tags every record with dataset_kind = "model_cams".
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(HOURLY_VARS),
        "past_days": past_days,
        "timezone": tz,
    }

    headers = {"User-Agent": "AirCue/0.1.0 (B.Tech Major Project; Contact: yusufmalu@example.com)"}

    with httpx.Client(timeout=30.0) as client:
        resp = client.get(OPEN_METEO_AQI_URL, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    fetch_ts = datetime.now().astimezone().isoformat()

    rows: list[dict[str, Any]] = []
    for i, t_str in enumerate(times):
        # Filter future timestamps: Open-Meteo hourly strings format: "YYYY-MM-DDTHH:00"
        # Since timezone is Asia/Kolkata, compare with current local time
        pm25 = hourly.get("pm2_5", [None])[i]
        pm10 = hourly.get("pm10", [None])[i]
        us_aqi = hourly.get("us_aqi", [None])[i]
        eu_aqi = hourly.get("european_aqi", [None])[i]
        o3 = hourly.get("ozone", [None])[i]
        no2 = hourly.get("nitrogen_dioxide", [None])[i]
        so2 = hourly.get("sulphur_dioxide", [None])[i]
        co = hourly.get("carbon_monoxide", [None])[i]

        cpcb_aqi = calculate_cpcb_aqi(pm25, pm10)
        cpcb_cat = aqi_to_category_cpcb(cpcb_aqi)

        rows.append({
            "timestamp": f"{t_str}:00+05:30",
            "location": location_name,
            "lat": lat,
            "lon": lon,
            "pm2_5": pm25,
            "pm10": pm10,
            "us_aqi": us_aqi,
            "european_aqi": eu_aqi,
            "ozone": o3,
            "no2": no2,
            "so2": so2,
            "co": co,
            "cpcb_aqi": cpcb_aqi,
            "cpcb_category": cpcb_cat,
            "provider": "open_meteo",
            "dataset_kind": "model_cams",
            "fetched_at": fetch_ts,
        })

    return rows
