"""Synthetic dataset generator for unit tests and CI only.

Synthetic data never enters production results or paper tables.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_synthetic_fixture(output_path: str | Path = "data/sample/sample_aqi.csv", n_hours: int = 72) -> Path:
    """Generate a tiny deterministic synthetic dataset for CI."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(seed=42)
    dates = pd.date_range("2026-01-01 00:00:00", periods=n_hours, freq="h", tz="Asia/Kolkata")

    # Generate synthetic PM profile with a moderate diurnal cycle
    base_pm25 = 45.0 + 35.0 * np.sin(np.linspace(0, 3 * np.pi, n_hours)) + rng.normal(0, 5, n_hours)
    base_pm25 = np.clip(base_pm25, 5.0, 350.0)

    rows = []
    for i, dt in enumerate(dates):
        pm25 = float(base_pm25[i])
        pm10 = float(pm25 * 1.8 + rng.normal(0, 5))
        rows.append({
            "timestamp": dt.isoformat(),
            "location": "Indore",
            "lat": 22.7196,
            "lon": 75.8577,
            "pm2_5": pm25,
            "pm10": pm10,
            "us_aqi": int(pm25 * 1.5),
            "european_aqi": 2,
            "ozone": 30.0,
            "no2": 25.0,
            "so2": 10.0,
            "co": 0.5,
            "cpcb_aqi": int(pm25 * 1.6),
            "cpcb_category": "Moderate" if pm25 < 90 else "Poor",
            "provider": "synthetic_mock",
            "dataset_kind": "synthetic_ci_only",
            "fetched_at": "2026-01-01T00:00:00+05:30",
        })

    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)
    return out
