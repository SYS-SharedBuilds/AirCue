"""Dataset inspection and summary tools."""
from __future__ import annotations

import pandas as pd
from rich.console import Console
from rich.table import Table


def inspect_dataset(df: pd.DataFrame) -> None:
    """Print structured summary and EDA metrics of dataset."""
    console = Console()
    if df.empty:
        console.print("[red]Dataset is empty.[/red]")
        return

    console.print(f"[bold green]Dataset Summary[/bold green] (Total rows: {len(df):,})")
    console.print(f"Time Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    console.print(f"Locations ({df['location'].nunique()}): {', '.join(sorted(df['location'].unique()))}")
    console.print(f"Data Kinds: {', '.join(df['dataset_kind'].unique())}")

    # Per-location breakdown
    loc_table = Table(title="Per-Location Metrics")
    loc_table.add_column("Location", style="cyan")
    loc_table.add_column("Rows", justify="right")
    loc_table.add_column("PM2.5 Mean ± Std", justify="right")
    loc_table.add_column("CPCB AQI Mean", justify="right")
    loc_table.add_column("Missing %", justify="right")

    for loc, grp in df.groupby("location"):
        pm_mean = grp["pm2_5"].mean()
        pm_std = grp["pm2_5"].std()
        aqi_mean = grp["cpcb_aqi"].mean()
        missing = grp["pm2_5"].isna().mean() * 100.0
        loc_table.add_row(
            str(loc),
            f"{len(grp):,}",
            f"{pm_mean:.1f} ± {pm_std:.1f}",
            f"{aqi_mean:.1f}",
            f"{missing:.1f}%",
        )
    console.print(loc_table)

    # Category distribution
    cat_table = Table(title="CPCB AQI Category Distribution")
    cat_table.add_column("Category", style="magenta")
    cat_table.add_column("Count", justify="right")
    cat_table.add_column("Percentage", justify="right")

    cats = df["cpcb_category"].value_counts()
    for cat, count in cats.items():
        pct = (count / len(df)) * 100.0
        cat_table.add_row(str(cat), f"{count:,}", f"{pct:.1f}%")
    console.print(cat_table)
