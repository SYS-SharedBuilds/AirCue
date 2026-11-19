"""Stratified benchmark scenarios generated from real snapshot data."""
from __future__ import annotations

import random
from typing import Any

import pandas as pd


def generate_task1_scenarios(snapshot_df: pd.DataFrame, n_samples: int = 160, seed: int = 42) -> list[dict[str, Any]]:
    """Generate balanced announcement generation scenarios stratified across levels, languages, tones, slots."""
    rng = random.Random(seed)
    languages = ["en", "hi"]
    tones = ["neutral", "young"]
    slots = ["assembly", "sports_pt", "recess", "dismissal", "general"]
    levels = [1, 2, 3, 4]

    # Sample realistic PM and AQI values from snapshot for each level
    level_pools: dict[int, list[dict[str, Any]]] = {lvl: [] for lvl in levels}
    for _, row in snapshot_df.dropna(subset=["pm2_5", "cpcb_aqi"]).iterrows():
        aqi = float(row["cpcb_aqi"])
        lvl = 0
        if aqi >= 401:
            lvl = 4
        elif aqi >= 301:
            lvl = 3
        elif aqi >= 201:
            lvl = 2
        elif aqi >= 101:
            lvl = 1

        if lvl in level_pools:
            level_pools[lvl].append({
                "pm25": round(float(row["pm2_5"]), 1),
                "aqi": int(aqi),
                "category": row.get("cpcb_category", "Moderate"),
                "site": row.get("location", "Indore"),
            })

    scenarios = []
    for i in range(n_samples):
        lvl = levels[i % len(levels)]
        pool = level_pools.get(lvl)
        data_point = rng.choice(pool) if pool else {"pm25": 85.0, "aqi": 180, "category": "Moderate", "site": "Indore"}

        scenarios.append({
            "scenario_id": f"s1_{i:04d}",
            "level": lvl,
            "category": data_point["category"],
            "aqi": data_point["aqi"],
            "pm25": data_point["pm25"],
            "site": data_point["site"],
            "language": languages[i % len(languages)],
            "tone": tones[(i // len(languages)) % len(tones)],
            "activity_slot": slots[(i // (len(languages) * len(tones))) % len(slots)],
        })

    return scenarios


def generate_task2_scenarios(snapshot_df: pd.DataFrame, n_samples: int = 100, window_hours: int = 6, seed: int = 42) -> list[dict[str, Any]]:
    """Generate sequence windows of readings for ground truth trigger decision evaluation."""
    rng = random.Random(seed)
    df = snapshot_df.dropna(subset=["cpcb_aqi", "pm2_5"]).copy()
    df["dt"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by=["location", "dt"]).reset_index(drop=True)

    locations = df["location"].unique()
    scenarios = []

    for i in range(n_samples):
        loc = rng.choice(locations)
        loc_df = df[df["location"] == loc].reset_index(drop=True)
        if len(loc_df) <= window_hours + 1:
            continue

        start_idx = rng.randint(0, len(loc_df) - window_hours - 1)
        window = loc_df.iloc[start_idx : start_idx + window_hours]
        latest_row = window.iloc[-1]

        latest_aqi = float(latest_row["cpcb_aqi"])
        # Ground truth deterministic logic
        ground_truth_speak = latest_aqi >= 101.0
        ground_truth_level = 0
        if latest_aqi >= 401:
            ground_truth_level = 4
        elif latest_aqi >= 301:
            ground_truth_level = 3
        elif latest_aqi >= 201:
            ground_truth_level = 2
        elif latest_aqi >= 101:
            ground_truth_level = 1

        window_data = [
            {
                "timestamp": str(r["timestamp"]),
                "pm2_5": round(float(r["pm2_5"]), 1),
                "cpcb_aqi": int(r["cpcb_aqi"]),
            }
            for _, r in window.iterrows()
        ]

        scenarios.append({
            "scenario_id": f"s2_{i:04d}",
            "location": loc,
            "window": window_data,
            "ground_truth": {
                "speak": ground_truth_speak,
                "level": ground_truth_level,
                "event": "escalate" if ground_truth_speak else "none",
            },
        })

    return scenarios
