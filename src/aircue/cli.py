"""AirCue CLI entrypoint."""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

import pandas as pd
import typer
from rich.console import Console

from aircue.benchmark.metrics import compute_metrics
from aircue.benchmark.quota import QuotaManager
from aircue.benchmark.report import generate_benchmark_reports
from aircue.benchmark.runner import run_benchmark_suite
from aircue.config import load_config, load_yaml
from aircue.control.service import AirCueService
from aircue.control.sim_node import run_simulated_node
from aircue.data.cleaning import clean_dataframe
from aircue.data.inspect import inspect_dataset
from aircue.data.providers.open_meteo import fetch_open_meteo_city
from aircue.data.store import load_latest_snapshot, save_snapshot
from aircue.data.synthetic import generate_synthetic_fixture
from aircue.llm.discovery import (
    discover_openrouter_models,
    resolve_benchmark_models,
    save_discovered_snapshot,
)
from aircue.replay.plots import plot_aqi_timeline
from aircue.replay.replay import run_historical_replay
from aircue.transport.sources import ApiPollSource, CsvReplaySource

app = typer.Typer(
    name="aircue",
    help="AirCue: Outdoor Air-Quality Voice Announcer & LLM Benchmark System",
    add_completion=False,
)

data_app = typer.Typer(help="Manage and inspect air-quality datasets")
models_app = typer.Typer(help="Discover and snapshot LLM models")
benchmark_app = typer.Typer(help="Run and analyze LLM benchmarks")
clips_app = typer.Typer(help="Pregenerate and test audio clips")

app.add_typer(data_app, name="data")
app.add_typer(models_app, name="models")
app.add_typer(benchmark_app, name="benchmark")
app.add_typer(clips_app, name="clips")


@data_app.command("fetch")
def data_fetch(
    past_days: int = typer.Option(92, "--past-days", "-d", help="Historical days (max 92)"),
    config_file: str = typer.Option("configs/locations.yaml", "--locations", "-l"),
) -> None:
    """Fetch air-quality data from keyless Open-Meteo API for configured cities."""
    console = Console()
    loc_data = load_yaml(config_file)
    locations = loc_data.get("locations", {})
    if not locations:
        console.print("[red]No locations found in configuration.[/red]")
        raise typer.Exit(code=1)

    all_rows = []
    for loc_key, info in locations.items():
        name = info.get("name", loc_key)
        lat = info.get("latitude")
        lon = info.get("longitude")
        tz = info.get("timezone", "Asia/Kolkata")
        console.print(f"Fetching {past_days} days for [cyan]{name}[/cyan] ({lat}, {lon})...")
        try:
            rows = fetch_open_meteo_city(lat, lon, name, past_days=past_days, tz=tz)
            all_rows.extend(rows)
            console.print(f"  Fetched {len(rows)} hourly records for {name}.")
            time.sleep(0.5)  # Respect rate limits
        except Exception as e:
            console.print(f"[red]Error fetching {name}: {e}[/red]")

    df = pd.DataFrame(all_rows)
    cleaned_df = clean_dataframe(df)
    csv_path, manifest_path = save_snapshot(cleaned_df)
    console.print(f"[green]Snapshot saved successfully:[/green] {csv_path}")
    console.print(f"[green]Manifest:[/green] {manifest_path}")


@data_app.command("update")
def data_update(
    past_days: int = typer.Option(7, "--past-days", "-d", help="Past days to append/sync"),
    config_file: str = typer.Option("configs/locations.yaml", "--locations", "-l"),
) -> None:
    """Incrementally update dataset with recent days and deduplicate."""
    console = Console()
    try:
        existing_df = load_latest_snapshot()
    except Exception:
        existing_df = pd.DataFrame()

    loc_data = load_yaml(config_file)
    locations = loc_data.get("locations", {})
    new_rows = []
    for loc_key, info in locations.items():
        name = info.get("name", loc_key)
        lat = info.get("latitude")
        lon = info.get("longitude")
        tz = info.get("timezone", "Asia/Kolkata")
        console.print(f"Updating recent data for {name}...")
        try:
            rows = fetch_open_meteo_city(lat, lon, name, past_days=past_days, tz=tz)
            new_rows.extend(rows)
            time.sleep(0.5)
        except Exception as e:
            console.print(f"[yellow]Warning: {name} update failed: {e}[/yellow]")

    combined_df = pd.concat([existing_df, pd.DataFrame(new_rows)], ignore_index=True)
    cleaned = clean_dataframe(combined_df)
    csv_path, manifest_path = save_snapshot(cleaned)
    console.print(f"[green]Dataset updated. Total rows: {len(cleaned):,}[/green]")


@data_app.command("inspect")
def data_inspect(
    snapshot_csv: str = typer.Option("", "--file", "-f", help="Specific CSV snapshot to inspect"),
) -> None:
    """Inspect and print summary EDA statistics of latest snapshot."""
    if snapshot_csv:
        df = pd.read_csv(snapshot_csv)
    else:
        df = load_latest_snapshot()
    inspect_dataset(df)


@data_app.command("sample")
def data_sample() -> None:
    """Generate small synthetic fixture for CI."""
    p = generate_synthetic_fixture()
    typer.echo(f"Generated sample fixture: {p}")


@models_app.command("discover")
def models_discover(
    config_file: str = typer.Option("configs/benchmark.yaml", "--config", "-c"),
) -> None:
    """Discover available models on OpenRouter, filter by ADR-003 rules, and save snapshot."""
    console = Console()
    cfg = load_yaml(config_file)
    sel = cfg.get("selection", {})
    preferred = sel.get("preferred_families", ["deepseek", "moonshotai"])
    min_models = sel.get("min_models", 4)
    allow_paid = sel.get("allow_paid_preferred", False)

    console.print("[cyan]Querying OpenRouter API for available models...[/cyan]")
    raw_models = discover_openrouter_models()
    if not raw_models:
        console.print("[yellow]Could not reach live OpenRouter or no key provided; using fallback directory.[/yellow]")

    resolved = resolve_benchmark_models(
        raw_models,
        preferred_families=preferred,
        min_models=min_models,
        allow_paid_preferred=allow_paid,
    )

    console.print(f"[bold green]Resolved {len(resolved)} benchmark candidate models:[/bold green]")
    for m in resolved:
        pricing = m.get("pricing", {})
        p_cost = pricing.get("prompt", 0)
        c_cost = pricing.get("completion", 0)
        console.print(f" - [bold]{m.get('id')}[/bold] (Context: {m.get('context_length')}, Cost: {p_cost}/{c_cost})")

    # Check if preferred families are present
    has_preferred = any(any(fam in m.get("id", "").lower() for fam in preferred) for m in resolved)
    if not has_preferred:
        console.print(
            "\n[yellow]Notice: Neither DeepSeek nor Moonshot/Kimi currently have free models on OpenRouter.\n"
            "Benchmarking will proceed on established open-weight models (Google Gemma, NVIDIA Nemotron).\n"
            "To evaluate DeepSeek and Kimi, enable 'allow_paid_preferred: true' in configs/benchmark.yaml\n"
            "or configure direct provider API keys (DEEPSEEK_API_KEY / MOONSHOT_API_KEY).[/yellow]"
        )

    out_path = save_discovered_snapshot(resolved)
    console.print(f"\n[green]Saved discovered model snapshot:[/green] {out_path}")


@benchmark_app.command("plan")
def benchmark_plan(
    config_file: str = typer.Option("configs/benchmark.yaml", "--config", "-c"),
) -> None:
    """Calculate total benchmark requests and estimated run days under daily quota."""
    console = Console()
    cfg = load_yaml(config_file)
    quota_cfg = cfg.get("quota", {})
    budget = quota_cfg.get("daily_request_budget", 180)
    tasks_cfg = cfg.get("tasks", {})
    t1_samples = tasks_cfg.get("task1_generation", {}).get("samples_per_model", 160)
    t2_samples = tasks_cfg.get("task2_decision", {}).get("samples_per_model", 100)
    num_models = cfg.get("selection", {}).get("min_models", 4)

    total_per_model = t1_samples + t2_samples
    total_calls = total_per_model * num_models
    days_needed = (total_calls + budget - 1) // budget

    qm = QuotaManager(daily_budget=budget)
    calls_today = qm.get_calls_today()
    remaining_today = qm.remaining_today()

    console.print("[bold green]AirCue Benchmark Execution Plan[/bold green]")
    console.print(f"Target Models: {num_models}")
    console.print(f"Task 1 (Generation) samples per model: {t1_samples}")
    console.print(f"Task 2 (Decision) samples per model: {t2_samples}")
    console.print(f"Total calls per model: {total_per_model}")
    console.print(f"Total benchmark API calls: [bold]{total_calls}[/bold]")
    console.print(f"Configured Daily Request Budget: [bold]{budget}[/bold]")
    console.print(f"Calls made today (UTC): {calls_today} (Remaining: {remaining_today})")
    console.print(f"Projected Run Duration: [bold yellow]{days_needed} days[/bold yellow] under free-tier quota.")
    console.print(
        "[dim]Note: A one-time $10 OpenRouter top-up reportedly raises the daily limit to ~1,000/day,\n"
        "allowing the entire benchmark to finish in a single day.[/dim]"
    )


@benchmark_app.command("run")
def benchmark_run(
    mock: bool = typer.Option(False, "--mock", help="Run with deterministic mock client (offline)"),
    limit: int | None = typer.Option(None, "--limit", "-n", help="Cap samples per task for quick run"),
) -> None:
    """Run benchmark evaluation suite."""
    console = Console()
    console.print(f"[bold cyan]Starting AirCue Benchmark Suite (Mock={mock}, Limit={limit})...[/bold cyan]")
    results = asyncio.run(run_benchmark_suite(use_mock=mock, limit=limit))
    console.print(f"[bold green]Benchmark run complete. Processed {len(results)} items.[/bold green]")
    console.print("Reports generated into 'results/report/' and 'paper/tables/'.")


@benchmark_app.command("report")
def benchmark_report(
    raw_log: str = typer.Option("results/raw/latest_run.jsonl", "--raw-log", "-r"),
) -> None:
    """Generate reports and publication tables from raw benchmark run log."""
    console = Console()
    raw_path = Path(raw_log)
    if not raw_path.exists():
        console.print(f"[red]Raw log file '{raw_log}' not found. Run benchmark first.[/red]")
        raise typer.Exit(code=1)

    raw_results = []
    with open(raw_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                raw_results.append(json.loads(line))

    metrics = compute_metrics(raw_results)
    generate_benchmark_reports(raw_results, metrics)
    console.print(f"[green]Successfully generated reports from {len(raw_results)} records.[/green]")


@app.callback()
def main() -> None:
    """AirCue: Event-driven outdoor school voice alert system."""


@app.command("run")
def service_run(
    source: str = typer.Option("replay", "--source", "-s", help="Telemetry source: replay, api, or mqtt"),
    location: str = typer.Option("Indore", "--location", "-l", help="Location name"),
    speed: float = typer.Option(5.0, "--speed", help="Replay speed factor"),
    config_file: str = typer.Option("configs/aircue.yaml", "--config", "-c"),
) -> None:
    """Run AirCue speech alert service."""
    console = Console()
    cfg = load_config(config_file)
    console.print(f"[bold green]Starting AirCue Service[/bold green] (Site: {cfg.site.id}, Source: {source})")

    if source == "replay":
        try:
            snapshot_path = sorted(Path("data/snapshots").glob("aqi_snapshot_*.csv"))[-1]
        except Exception:
            snapshot_path = Path("data/sample/sample_aqi.csv")
        telemetry_source = CsvReplaySource(str(snapshot_path), location=location, speed=speed)
    elif source == "api":
        telemetry_source = ApiPollSource(lat=22.7196, lon=75.8577, location=location)
    else:
        # Default fallback to replay for local demo
        snapshot_path = sorted(Path("data/snapshots").glob("aqi_snapshot_*.csv"))[-1]
        telemetry_source = CsvReplaySource(str(snapshot_path), location=location, speed=speed)

    svc = AirCueService(config=cfg, source=telemetry_source)
    svc.run()


@app.command("sim-node")
def sim_node_cmd(
    site: str = typer.Option("indore_school_01", "--site", "-s"),
    interval: float = typer.Option(2.0, "--interval", "-i"),
    count: int = typer.Option(0, "--count", "-n", help="Number of telemetry packets to send (0 = infinite)"),
) -> None:
    """Run simulated outdoor sensor node publishing telemetry over MQTT."""
    run_simulated_node(site=site, interval_seconds=interval, count=count)


@app.command("replay")
def replay_cmd(
    location: str = typer.Option("Indore", "--location", "-l"),
) -> None:
    """Run state machine replay over dataset snapshot and analyze trigger cadence."""
    console = Console()
    snapshot_path = sorted(Path("data/snapshots").glob("aqi_snapshot_*.csv"))[-1]
    console.print(f"[bold cyan]Running Historical Replay for '{location}'...[/bold cyan]")
    res = run_historical_replay(snapshot_path, location=location)

    console.print(f"Total Spoken / Suppressed Events: [bold]{res['total_events']}[/bold]")
    console.print(f"Average Announcements / Day: [bold]{res['announcements_per_day']:.2f}[/bold]")
    console.print("Event breakdown:")
    for kind, count in res["event_counts"].items():
        console.print(f" - {kind}: {count}")

    plot_path = plot_aqi_timeline(snapshot_path, location=location)
    console.print(f"[green]Saved timeline plot:[/green] {plot_path}")


@app.command("tune")
def tune_cmd(
    location: str = typer.Option("Indore", "--location", "-l"),
) -> None:
    """Run parameter tuning grid over thresholds to evaluate cadence against target range."""
    console = Console()
    snapshot_path = sorted(Path("data/snapshots").glob("aqi_snapshot_*.csv"))[-1]
    console.print(f"[bold cyan]Tuning confirmation windows for '{location}'...[/bold cyan]")

    for confirm_sec in [1800, 3600, 7200]:
        cfg = load_config()
        cfg.trigger.confirm_seconds = confirm_sec
        res = run_historical_replay(snapshot_path, location=location, config=cfg)
        console.print(
            f"Confirm: {confirm_sec // 60}m -> Events: {res['total_events']}, "
            f"Per Day: {res['announcements_per_day']:.2f}"
        )


if __name__ == "__main__":
    app()
