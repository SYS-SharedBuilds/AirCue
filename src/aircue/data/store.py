"""Dataset storage, snapshot management, and SHA-256 provenance manifests."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd


def compute_sha256(file_path: str | Path) -> str:
    """Compute SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def save_snapshot(
    df: pd.DataFrame,
    snapshots_dir: str | Path = "data/snapshots",
    date_str: Optional[str] = None,
) -> tuple[Path, Path]:
    """Save cleaned dataframe as a committed snapshot CSV and corresponding JSON manifest."""
    out_dir = Path(snapshots_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    csv_path = out_dir / f"aqi_snapshot_{date_str}.csv"
    manifest_path = out_dir / f"aqi_snapshot_{date_str}.json"

    df.to_csv(csv_path, index=False)
    sha = compute_sha256(csv_path)

    manifest: Dict[str, Any] = {
        "snapshot_date": date_str,
        "csv_filename": csv_path.name,
        "sha256": sha,
        "row_count": len(df),
        "locations": sorted(df["location"].unique().tolist()) if not df.empty else [],
        "min_timestamp": str(df["timestamp"].min()) if not df.empty else None,
        "max_timestamp": str(df["timestamp"].max()) if not df.empty else None,
        "providers": sorted(df["provider"].unique().tolist()) if not df.empty else [],
        "dataset_kind": sorted(df["dataset_kind"].unique().tolist()) if not df.empty else [],
        "category_distribution": df["cpcb_category"].value_counts().to_dict() if not df.empty else {},
        "created_at": datetime.now().astimezone().isoformat(),
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return csv_path, manifest_path


def load_latest_snapshot(snapshots_dir: str | Path = "data/snapshots") -> pd.DataFrame:
    """Load the latest snapshot CSV found in snapshots_dir."""
    p = Path(snapshots_dir)
    csv_files = sorted(p.glob("aqi_snapshot_*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No snapshot CSV files found in {snapshots_dir}")
    return pd.read_csv(csv_files[-1])
