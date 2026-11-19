"""Timeline plotting tools for air quality and announcements."""
from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def plot_aqi_timeline(
    csv_path: str | Path,
    location: str = "Indore",
    output_dir: str | Path = "results/replay",
) -> Path:
    """Plot AQI timeline with CPCB alert bands."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"aqi_timeline_{location.lower()}.png"

    df = pd.read_csv(csv_path)
    if "location" in df.columns:
        df = df[df["location"].str.lower() == location.lower()].copy()

    df["dt"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by="dt")

    plt.figure(figsize=(12, 5))
    plt.plot(df["dt"], df["cpcb_aqi"], label="CPCB AQI", color="#2c3e50", linewidth=1.2)

    # Shaded level bands
    plt.axhspan(0, 50, color="#2ecc71", alpha=0.15, label="Good (0-50)")
    plt.axhspan(51, 100, color="#a3e048", alpha=0.15, label="Satisfactory (51-100)")
    plt.axhspan(101, 200, color="#f1c40f", alpha=0.15, label="Moderate (101-200)")
    plt.axhspan(201, 300, color="#e67e22", alpha=0.15, label="Poor (201-300)")
    plt.axhspan(301, 400, color="#e74c3c", alpha=0.15, label="Very Poor (301-400)")
    plt.axhspan(401, 500, color="#962d3e", alpha=0.15, label="Severe (401+)")

    plt.title(f"Air Quality Index Timeline — {location.capitalize()} (Past 92 Days)")
    plt.xlabel("Date")
    plt.ylabel("CPCB AQI")
    plt.ylim(0, 500)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize="small")
    plt.tight_layout()
    plt.savefig(out_file, dpi=200)
    plt.close()

    return out_file
