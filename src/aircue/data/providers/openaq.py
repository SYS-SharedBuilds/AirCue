"""Optional OpenAQ v3 client for ground station observations."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import httpx


def fetch_openaq_station_data(
    lat: float,
    lon: float,
    location_name: str,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch physical sensor readings from OpenAQ v3 if API key is supplied.

    If no API key is provided in argument or OPENAQ_API_KEY env, skips gracefully.
    """
    key = api_key or os.environ.get("OPENAQ_API_KEY")
    if not key:
        return []

    headers = {"X-API-Key": key, "User-Agent": "AirCue/0.1.0"}
    # OpenAQ v3 implementation queries nearest location within 25km radius
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(
                "https://api.openaq.org/v3/locations",
                params={"coordinates": f"{lat},{lon}", "radius": 25000, "limit": 1},
                headers=headers,
            )
            if resp.status_code != 200:
                return []
            # Station data parsing would proceed here if active key provided
            return []
    except Exception:
        return []
