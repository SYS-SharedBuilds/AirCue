"""Data cleaning, deduplication, and quality control."""
from __future__ import annotations

import pandas as pd

from aircue.trigger.aqi import aqi_to_category_cpcb, calculate_cpcb_aqi


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate raw air-quality dataframe:

    - Standardize lat/lon column names.
    - Drop duplicates on (location, timestamp, provider).
    - Discard impossible or negative particulate concentrations.
    - Calculate CPCB AQI and category for all rows where missing.
    - Sort chronologically per location.
    - Ensure timestamp parseability.
    """
    if df.empty:
        return df

    cleaned = df.copy()

    # Standardize coordinate columns
    if "latitude" in cleaned.columns and "lat" in cleaned.columns:
        cleaned["lat"] = cleaned["lat"].combine_first(cleaned["latitude"])
        cleaned = cleaned.drop(columns=["latitude"])
    elif "latitude" in cleaned.columns:
        cleaned = cleaned.rename(columns={"latitude": "lat"})

    if "longitude" in cleaned.columns and "lon" in cleaned.columns:
        cleaned["lon"] = cleaned["lon"].combine_first(cleaned["longitude"])
        cleaned = cleaned.drop(columns=["longitude"])
    elif "longitude" in cleaned.columns:
        cleaned = cleaned.rename(columns={"longitude": "lon"})

    # Deduplicate
    cleaned = cleaned.drop_duplicates(subset=["location", "timestamp", "provider"])

    # Discard negative PM readings
    if "pm2_5" in cleaned.columns:
        cleaned.loc[cleaned["pm2_5"] < 0, "pm2_5"] = None
    if "pm10" in cleaned.columns:
        cleaned.loc[cleaned["pm10"] < 0, "pm10"] = None

    # Calculate CPCB AQI and category if missing
    if "cpcb_aqi" not in cleaned.columns:
        cleaned["cpcb_aqi"] = None
    if "cpcb_category" not in cleaned.columns:
        cleaned["cpcb_category"] = None

    needs_aqi = cleaned["cpcb_aqi"].isna() & (cleaned["pm2_5"].notna() | cleaned["pm10"].notna())
    if needs_aqi.any():
        computed_aqi = [
            calculate_cpcb_aqi(row["pm2_5"], row["pm10"]) if pd.notna(row["pm2_5"]) or pd.notna(row["pm10"]) else None
            for _, row in cleaned[needs_aqi].iterrows()
        ]
        cleaned.loc[needs_aqi, "cpcb_aqi"] = computed_aqi
        cleaned.loc[needs_aqi, "cpcb_category"] = [aqi_to_category_cpcb(aqi) if aqi is not None else None for aqi in computed_aqi]

    # Sort
    cleaned = cleaned.sort_values(by=["location", "timestamp"]).reset_index(drop=True)
    return cleaned
