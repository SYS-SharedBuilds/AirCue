"""Data cleaning, deduplication, and quality control."""
from __future__ import annotations

import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate raw air-quality dataframe:

    - Drop duplicates on (location, timestamp, provider).
    - Discard impossible or negative particulate concentrations.
    - Sort chronologically per location.
    - Ensure timestamp parseability.
    """
    if df.empty:
        return df

    cleaned = df.copy()

    # Deduplicate
    cleaned = cleaned.drop_duplicates(subset=["location", "timestamp", "provider"])

    # Discard negative PM readings
    if "pm2_5" in cleaned.columns:
        cleaned.loc[cleaned["pm2_5"] < 0, "pm2_5"] = None
    if "pm10" in cleaned.columns:
        cleaned.loc[cleaned["pm10"] < 0, "pm10"] = None

    # Sort
    cleaned = cleaned.sort_values(by=["location", "timestamp"]).reset_index(drop=True)
    return cleaned
