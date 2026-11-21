"""Bridge script providing JSON API support to Node.js backend."""
from __future__ import annotations

import asyncio
import io
import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from gtts import gTTS

from aircue.data.store import load_latest_snapshot
from aircue.llm.dataset_agent import answer_dataset_chat
from aircue.llm.openrouter import OpenRouterClient
from aircue.llm.parsing import parse_json_robust
from aircue.llm.prompts import (
    SYSTEM_PROMPT_ANNOUNCEMENT,
    SYSTEM_PROMPT_DECISION,
    build_announcement_user_prompt,
    build_decision_user_prompt,
)
from aircue.llm.validators import validate_announcement
from aircue.messages.builder import build_message
from aircue.trigger.aqi import aqi_to_category_cpcb
from aircue.trigger.engine import Event

load_dotenv()


def handle_locations() -> dict[str, Any]:
    df = load_latest_snapshot()
    locs = []
    grouped = df.groupby("location").first().reset_index()
    for _, row in grouped.iterrows():
        locs.append({
            "name": row["location"],
            "lat": row.get("lat"),
            "lon": row.get("lon"),
            "dataset_kind": row.get("dataset_kind", "model_cams"),
            "provider": row.get("provider", "open_meteo"),
        })
    return {"locations": sorted(locs, key=lambda x: x["name"])}


def handle_telemetry(location: str, limit: int = 150) -> dict[str, Any]:
    df = load_latest_snapshot()
    subset = df[df["location"] == location].copy()
    if subset.empty:
        return {"error": f"Location {location} not found", "records": []}
    subset["dt"] = pd.to_datetime(subset["timestamp"])
    subset = subset.sort_values(by="dt")
    records = []
    for _, r in subset.tail(limit).iterrows():
        records.append({
            "timestamp": str(r["timestamp"]),
            "dt": r["dt"].strftime("%Y-%m-%d %H:%M"),
            "pm2_5": float(r["pm2_5"]) if pd.notna(r.get("pm2_5")) else None,
            "pm10": float(r["pm10"]) if pd.notna(r.get("pm10")) else None,
            "cpcb_aqi": float(r["cpcb_aqi"]) if pd.notna(r.get("cpcb_aqi")) else None,
            "cpcb_category": str(r.get("cpcb_category", "")),
        })
    stats = {
        "mean_pm25": round(float(subset["pm2_5"].mean()), 1) if not subset["pm2_5"].isna().all() else None,
        "mean_aqi": round(float(subset["cpcb_aqi"].mean()), 1) if not subset["cpcb_aqi"].isna().all() else None,
        "max_aqi": round(float(subset["cpcb_aqi"].max()), 1) if not subset["cpcb_aqi"].isna().all() else None,
        "total_rows": len(subset),
        "dataset_kind": subset["dataset_kind"].iloc[0] if "dataset_kind" in subset.columns else "model_cams",
    }
    return {"location": location, "stats": stats, "records": records}


async def handle_generate_announcement(data: dict[str, Any]) -> dict[str, Any]:
    model = data.get("model", "deepseek/deepseek-chat")
    api_key = data.get("api_key") or os.environ.get("OPENROUTER_API_KEY", "")
    level = int(data.get("level", 2))
    aqi_val = float(data.get("aqi", 220))
    pm25_val = float(data.get("pm25", 95.0))
    slot = data.get("slot", "Sports PT")
    language = data.get("language", "hi")
    site = data.get("site", "School Campus Ground, Indore")
    temperature = float(data.get("temperature", 0.7))

    facts = {
        "level": level,
        "category": aqi_to_category_cpcb(aqi_val),
        "aqi": aqi_val,
        "pm25": pm25_val,
        "site": site,
        "activity_slot": slot,
        "language": language,
        "tone": "authoritative and polite",
    }

    client = OpenRouterClient(model=model, api_key=api_key)
    prompt = build_announcement_user_prompt(facts)
    res = await client.complete(
        prompt,
        system_prompt=SYSTEM_PROMPT_ANNOUNCEMENT,
        temperature=temperature,
        max_tokens=250,
    )

    if res.raw_error:
        return {"error": res.raw_error, "model": model}

    val = validate_announcement(res.text, expected_lang=language, input_facts=facts)
    clean_text = res.text.strip()

    # Generate audio base64 using gTTS for playback in web app
    audio_base64 = None
    try:
        import base64
        tts = gTTS(text=clean_text, lang=language)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        audio_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        audio_base64 = None

    return {
        "model": model,
        "latency_s": round(res.latency_s, 2),
        "raw_text": res.text,
        "clean_text": clean_text,
        "facts": facts,
        "validation": {
            "passed": val.passed,
            "rules": val.rule_results,
            "failures": val.failure_reasons,
        },
        "audio_base64": audio_base64,
    }


async def handle_generate_decision(data: dict[str, Any]) -> dict[str, Any]:
    model = data.get("model", "deepseek/deepseek-chat")
    api_key = data.get("api_key") or os.environ.get("OPENROUTER_API_KEY", "")
    history = data.get("history", [])
    current_state = data.get("current_state", {"level": 0, "minutes_since_last": 120})

    client = OpenRouterClient(model=model, api_key=api_key)
    prompt = build_decision_user_prompt(history, current_state)
    res = await client.complete(
        prompt,
        system_prompt=SYSTEM_PROMPT_DECISION,
        temperature=0.0,
        max_tokens=200,
    )

    if res.raw_error:
        return {"error": res.raw_error, "model": model}

    parsed = parse_json_robust(res.text)
    return {
        "model": model,
        "latency_s": round(res.latency_s, 2),
        "raw_text": res.text,
        "parsed": parsed,
    }


async def handle_chat_conversational(data: dict[str, Any]) -> dict[str, Any]:
    messages = data.get("messages", [])
    model = data.get("model", "deepseek/deepseek-chat")
    api_key = data.get("api_key") or os.environ.get("OPENROUTER_API_KEY", "")
    temperature = float(data.get("temperature", 0.5))

    return await answer_dataset_chat(
        messages=messages,
        model=model,
        api_key=api_key,
        temperature=temperature,
    )


def handle_clip_preview(data: dict[str, Any]) -> dict[str, Any]:
    level = int(data.get("level", 2))
    kind = data.get("kind", "escalate")
    language = data.get("language", "hi")
    slot = data.get("slot")
    aqi_val = float(data.get("aqi", 220))

    ev = Event(kind=kind, level=level, timestamp=0.0, aqi=aqi_val)
    msg = build_message(ev, language=language, slot=slot if slot != "general" else None)

    clip_file = Path("clips") / f"{msg.clip_id}.wav"
    exists = clip_file.exists()

    return {
        "clip_id": msg.clip_id,
        "text": msg.text,
        "language": language,
        "level": level,
        "kind": kind,
        "slot": slot,
        "exists": exists,
        "clip_url": f"/clips/{msg.clip_id}.wav" if exists else None,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        return

    action = sys.argv[1]
    raw_payload = sys.argv[2] if len(sys.argv) > 2 else "{}"
    try:
        payload = json.loads(raw_payload)
    except Exception:
        payload = {}

    if action == "locations":
        print(json.dumps(handle_locations()))
    elif action == "telemetry":
        loc = payload.get("location", "Indore")
        limit = int(payload.get("limit", 150))
        print(json.dumps(handle_telemetry(loc, limit)))
    elif action == "generate_announcement":
        res = asyncio.run(handle_generate_announcement(payload))
        print(json.dumps(res))
    elif action == "chat_conversational":
        res = asyncio.run(handle_chat_conversational(payload))
        print(json.dumps(res))
    elif action == "generate_decision":
        res = asyncio.run(handle_generate_decision(payload))
        print(json.dumps(res))
    elif action == "clip_preview":
        print(json.dumps(handle_clip_preview(payload)))
    elif action == "status":
        quota_path = Path("results/quota.json")
        quota = {}
        if quota_path.exists():
            with open(quota_path) as f:
                quota = json.load(f)
        print(json.dumps({
            "status": "online",
            "has_openrouter_key": bool(os.environ.get("OPENROUTER_API_KEY")),
            "has_openaq_key": bool(os.environ.get("OPENAQ_API_KEY")),
            "quota": quota,
        }))
    else:
        print(json.dumps({"error": f"Unknown action: {action}"}))


if __name__ == "__main__":
    main()
