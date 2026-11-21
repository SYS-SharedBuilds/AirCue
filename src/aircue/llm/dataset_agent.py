"""Conversational intelligence agent specifically grounded over the Madhya Pradesh AQI dataset."""
from __future__ import annotations

import re
from typing import Any

import pandas as pd
from dotenv import load_dotenv

from aircue.data.store import load_latest_snapshot
from aircue.llm.openrouter import OpenRouterClient

load_dotenv()

# Module-level cache for dataset and locations list
_CACHED_DF: pd.DataFrame | None = None
_KNOWN_LOCATIONS: list[str] = []


def get_dataset() -> pd.DataFrame:
    """Return cached snapshot dataframe."""
    global _CACHED_DF, _KNOWN_LOCATIONS
    if _CACHED_DF is None:
        _CACHED_DF = load_latest_snapshot()
        _KNOWN_LOCATIONS = sorted(_CACHED_DF["location"].dropna().unique().tolist())
    return _CACHED_DF


def get_known_locations() -> list[str]:
    """Return all known location names in the MP dataset."""
    get_dataset()
    return _KNOWN_LOCATIONS


def compute_dataset_summary() -> dict[str, Any]:
    """Compute overall state-wide dataset statistics."""
    df = get_dataset()
    cat_counts = df["cpcb_category"].value_counts().to_dict()
    mean_aqi_by_loc = df.groupby("location")["cpcb_aqi"].mean().dropna()

    worst_5 = [
        {"location": loc, "mean_aqi": round(float(val), 1)}
        for loc, val in mean_aqi_by_loc.sort_values(ascending=False).head(5).items()
    ]
    cleanest_5 = [
        {"location": loc, "mean_aqi": round(float(val), 1)}
        for loc, val in mean_aqi_by_loc.sort_values().head(5).items()
    ]

    max_aqi_row = df.loc[df["cpcb_aqi"].idxmax()] if not df["cpcb_aqi"].isna().all() else None
    peak_info = None
    if max_aqi_row is not None:
        peak_info = {
            "location": max_aqi_row["location"],
            "aqi": round(float(max_aqi_row["cpcb_aqi"]), 1),
            "pm2_5": round(float(max_aqi_row["pm2_5"]), 1) if pd.notna(max_aqi_row.get("pm2_5")) else None,
            "timestamp": str(max_aqi_row["timestamp"]),
        }

    return {
        "total_records": len(df),
        "total_locations": len(_KNOWN_LOCATIONS),
        "category_distribution": cat_counts,
        "worst_5_locations": worst_5,
        "cleanest_5_locations": cleanest_5,
        "peak_recorded_aqi": peak_info,
        "state": "Madhya Pradesh, India",
    }


def find_mentioned_locations(text: str) -> list[str]:
    """Identify which MP locations or cities are referenced in the input text."""
    locations = get_known_locations()
    text_lower = text.lower()
    matched = []

    # Direct substring search on full names
    for loc in locations:
        if loc.lower() in text_lower:
            matched.append(loc)

    # Search for base city/district names (e.g. "Indore", "Gwalior", "Jabalpur", "Bhopal", "Ujjain", "Satna")
    major_keys = [
        "indore", "bhopal", "jabalpur", "gwalior", "ujjain", "dewas", "sagar", "satna",
        "singrauli", "ratlam", "katni", "rewa", "burhanpur", "morena", "damoh", "vidisha",
        "chhindwara", "seoni", "mandsaur", "neemuch", "khargone", "khandwa", "pithampur",
        "mandideep", "vijay nagar", "chhoti gwaltoli", "mahakaleshwar", "mahashweta"
    ]
    for key in major_keys:
        if re.search(rf"\b{re.escape(key)}\b", text_lower):
            for loc in locations:
                if key in loc.lower() and loc not in matched:
                    matched.append(loc)

    # Limit to top 6 most relevant matches to keep prompt focused
    return matched[:6]


def get_location_stats(location: str) -> dict[str, Any] | None:
    """Extract summary metrics and recent readings for a specific location."""
    df = get_dataset()
    sub = df[df["location"] == location].copy()
    if sub.empty:
        return None

    sub["dt"] = pd.to_datetime(sub["timestamp"])
    sub = sub.sort_values(by="dt")

    cats = sub["cpcb_category"].value_counts(normalize=True).to_dict()
    cat_pct = {k: f"{round(v * 100, 1)}%" for k, v in cats.items()}

    recent = []
    for _, r in sub.tail(3).iterrows():
        recent.append({
            "timestamp": str(r["timestamp"]),
            "pm2_5": round(float(r["pm2_5"]), 1) if pd.notna(r.get("pm2_5")) else None,
            "pm10": round(float(r["pm10"]), 1) if pd.notna(r.get("pm10")) else None,
            "aqi": round(float(r["cpcb_aqi"]), 1) if pd.notna(r.get("cpcb_aqi")) else None,
            "category": str(r.get("cpcb_category", "")),
        })

    return {
        "location": location,
        "dataset_kind": sub["dataset_kind"].iloc[0] if "dataset_kind" in sub.columns else "model_cams",
        "provider": sub["provider"].iloc[0] if "provider" in sub.columns else "unknown",
        "total_records": len(sub),
        "mean_aqi": round(float(sub["cpcb_aqi"].mean()), 1) if not sub["cpcb_aqi"].isna().all() else None,
        "max_aqi": round(float(sub["cpcb_aqi"].max()), 1) if not sub["cpcb_aqi"].isna().all() else None,
        "min_aqi": round(float(sub["cpcb_aqi"].min()), 1) if not sub["cpcb_aqi"].isna().all() else None,
        "mean_pm25": round(float(sub["pm2_5"].mean()), 1) if not sub["pm2_5"].isna().all() else None,
        "mean_pm10": round(float(sub["pm10"].mean()), 1) if not sub["pm10"].isna().all() else None,
        "category_percentages": cat_pct,
        "recent_readings": recent,
    }


def build_system_prompt_for_chat(matched_stats: list[dict[str, Any]]) -> str:
    """Build the grounded conversational system prompt."""
    summary = compute_dataset_summary()

    grounding_blocks = []
    if matched_stats:
        grounding_blocks.append("### Relevant Telemetry for Mentioned Locations:")
        for st in matched_stats:
            grounding_blocks.append(
                f"- **{st['location']}** ({st['dataset_kind']}, via {st['provider']}):\n"
                f"  Mean AQI: {st['mean_aqi']} | Max AQI: {st['max_aqi']} | Mean PM2.5: {st['mean_pm25']} µg/m³ | Mean PM10: {st['mean_pm10']} µg/m³\n"
                f"  Category Distribution: {st['category_percentages']}\n"
                f"  Latest Readings: {st['recent_readings']}"
            )
    else:
        grounding_blocks.append("### General Madhya Pradesh Dataset Overview:")
        grounding_blocks.append(
            f"- Total Observations: {summary['total_records']} rows across {summary['total_locations']} locations in Madhya Pradesh.\n"
            f"- Category Totals: {summary['category_distribution']}\n"
            f"- Highest Mean AQI Locations: {summary['worst_5_locations']}\n"
            f"- Cleanest Mean AQI Locations: {summary['cleanest_5_locations']}\n"
            f"- Peak Historical Spike: {summary['peak_recorded_aqi']}"
        )

    facts_text = "\n".join(grounding_blocks)

    return f"""You are the **AirCue Conversational Intelligence Model**, a specialized air quality AI assistant explicitly trained and grounded on the comprehensive Madhya Pradesh Air Quality Telemetry Dataset and Indian Central Pollution Control Board (CPCB) standards.

You are interacting with users inside the AirCue research and operational platform. Your style should be thoughtful, articulate, highly knowledgeable, and conversational, matching the refined editorial voice of Claude.ai.

### Verified Dataset Knowledge Base (Madhya Pradesh, India):
{facts_text}

### Official CPCB Air Quality Index (AQI) Scales & Guidelines:
1. **Good (0 - 50)**: Minimal impact. Full outdoor sports and normal school activities.
2. **Satisfactory (51 - 100)**: Minor breathing discomfort to sensitive people. Normal school sports permitted.
3. **Moderate (101 - 200)**: Breathing discomfort to people with asthma and heart diseases. Consider shortening intensive prolonged physical training.
4. **Poor (201 - 300)**: Breathing discomfort to most people on prolonged exposure. Substitute outdoor physical training (PT) with indoor activities; shorten morning assemblies.
5. **Very Poor (301 - 400)**: Respiratory illness on prolonged exposure. Suspend all strenuous outdoor sports and outdoor assemblies.
6. **Severe (401 - 500+)**: Severe health impacts even on healthy people. Immediate cancellation of all outdoor activities; remain indoors.

### Conversational Rules:
- Answer questions accurately citing the empirical figures and station metrics provided above.
- When comparing localities (e.g., Vijay Nagar vs Chhoti Gwaltoli in Indore), explain the differences in urban topology (commercial/traffic corridor vs residential/health zone).
- Emphasize practical school health precautions, outdoor physical training adjustments, and student safety.
- Strictly outdoor context: Do NOT suggest opening or closing classroom windows, ventilation shafts, or indoor HVAC filters unless specifically asked about buildings.
- Do not produce alarmist or panic-inducing medical diagnoses. Maintain a calm, authoritative, scientific tone.
"""


async def answer_dataset_chat(
    messages: list[dict[str, str]],
    model: str = "deepseek/deepseek-chat",
    api_key: str | None = None,
    temperature: float = 0.5,
) -> dict[str, Any]:
    """Process a conversational query over the MP AQI dataset with grounded context."""
    # Concatenate recent user messages to find referenced locations
    recent_user_text = " ".join(
        m.get("content", "") for m in messages if m.get("role") == "user"
    )
    matched_locs = find_mentioned_locations(recent_user_text)

    matched_stats = []
    for loc in matched_locs:
        st = get_location_stats(loc)
        if st:
            matched_stats.append(st)

    system_prompt = build_system_prompt_for_chat(matched_stats)

    client = OpenRouterClient(model=model, api_key=api_key)

    formatted_messages = [{"role": "system", "content": system_prompt}]
    for m in messages:
        if m.get("role") in ("user", "assistant"):
            formatted_messages.append({"role": m["role"], "content": m.get("content", "")})

    res = await client.complete_messages(
        messages=formatted_messages,
        temperature=temperature,
        max_tokens=600,
    )

    if res.raw_error:
        return {
            "error": res.raw_error,
            "model": model,
            "matched_locations": matched_locs,
        }

    return {
        "reply": res.text,
        "model": model,
        "latency_s": round(res.latency_s, 2),
        "matched_locations": matched_locs,
        "grounding_summary": [
            {
                "location": s["location"],
                "mean_aqi": s["mean_aqi"],
                "max_aqi": s["max_aqi"],
                "mean_pm25": s["mean_pm25"],
            }
            for s in matched_stats
        ],
    }
