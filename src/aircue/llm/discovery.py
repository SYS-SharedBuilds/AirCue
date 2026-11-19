"""Model discovery, filtering, and deterministic benchmark candidate resolution."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx


def discover_openrouter_models(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query OpenRouter /api/v1/models endpoint."""
    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    headers = {"User-Agent": "AirCue/0.1.0"}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.get("https://openrouter.ai/api/v1/models", headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", [])
    except Exception:
        pass
    return []


def resolve_benchmark_models(
    raw_models: List[Dict[str, Any]],
    preferred_families: List[str] = ("deepseek", "moonshotai"),
    min_models: int = 4,
    allow_paid_preferred: bool = False,
    exclude_keywords: List[str] = ("-preview", "preview", "-music", "-audio", "-vl", "-code", "-exp", "promo", "openrouter/free"),
) -> List[Dict[str, Any]]:
    """Apply ADR-003 model discovery filters:

    1. Drop tiny/sub-7B parameter models (e.g. lfm-1.7b).
    2. Drop preview, promo, music, vision-only, and code slugs.
    3. Check preferred families (deepseek, moonshotai/kimi).
    4. Top up to min_models with established open-weight families (Google Gemma, NVIDIA Nemotron).
    """
    free_candidates = []
    paid_preferred_candidates = []

    for m in raw_models:
        slug = m.get("id", "").lower()
        pricing = m.get("pricing", {})
        prompt_cost = float(pricing.get("prompt", 0) or 0)
        compl_cost = float(pricing.get("completion", 0) or 0)
        is_free = (":free" in slug) or (prompt_cost == 0.0 and compl_cost == 0.0)

        # Exclude keyword check
        if any(kw in slug for kw in exclude_keywords):
            continue

        # Exclude known tiny models (e.g., 1.7b, small)
        if "1.7b" in slug or "-small" in slug:
            continue

        if is_free:
            free_candidates.append(m)
        elif allow_paid_preferred and any(fam in slug for fam in preferred_families):
            paid_preferred_candidates.append(m)

    resolved: List[Dict[str, Any]] = []

    # Step 1: Look for free preferred models
    for m in free_candidates:
        slug = m.get("id", "").lower()
        if any(fam in slug for fam in preferred_families):
            if m not in resolved:
                resolved.append(m)

    # Step 2: If allow_paid_preferred is True and preferred models needed, take cheapest
    if allow_paid_preferred and len(resolved) < min_models:
        # Sort paid preferred by cost
        paid_preferred_candidates.sort(
            key=lambda x: (float(x.get("pricing", {}).get("prompt", 0)) + float(x.get("pricing", {}).get("completion", 0)))
        )
        for m in paid_preferred_candidates:
            if m not in resolved:
                resolved.append(m)
            if len(resolved) >= min_models:
                break

    # Step 3: Top up with established open-weight families (Google Gemma, NVIDIA Nemotron)
    established_keywords = ["gemma", "nemotron", "ling"]
    established_free = [
        m for m in free_candidates
        if any(kw in m.get("id", "").lower() for kw in established_keywords) and m not in resolved
    ]
    # Deterministic alphabetical sort
    established_free.sort(key=lambda x: x.get("id", ""))
    for m in established_free:
        resolved.append(m)
        if len(resolved) >= min_models:
            break

    # Step 4: Final top-up if still under min_models
    for m in sorted(free_candidates, key=lambda x: x.get("id", "")):
        if m not in resolved:
            resolved.append(m)
        if len(resolved) >= min_models:
            break

    return resolved[:min_models]


def save_discovered_snapshot(
    resolved_models: List[Dict[str, Any]],
    output_dir: str | Path = "results/models",
) -> Path:
    """Save resolved model snapshot JSON."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = out_dir / f"discovered_{date_str}.json"

    data = {
        "discovered_at": datetime.now().astimezone().isoformat(),
        "count": len(resolved_models),
        "models": [
            {
                "id": m.get("id"),
                "name": m.get("name", m.get("id")),
                "context_length": m.get("context_length"),
                "pricing": m.get("pricing"),
            }
            for m in resolved_models
        ],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return path
