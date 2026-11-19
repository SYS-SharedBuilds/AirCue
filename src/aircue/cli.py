"""AirCue CLI entrypoint."""
import typer
import time
from pathlib import Path
import pandas as pd
import typer
from rich.console import Console

from aircue.audio.clips import build_all_clips
from aircue.config import load_config, load_yaml
from aircue.data.cleaning import clean_dataframe
from aircue.data.inspect import inspect_dataset
from aircue.data.providers.open_meteo import fetch_open_meteo_city
from aircue.data.store import load_latest_snapshot, save_snapshot
from aircue.data.synthetic import generate_synthetic_fixture

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


@clips_app.command("build")
def clips_build(
    output_dir: str = typer.Option("clips", "--output-dir", "-o", help="Target audio directory"),
    backend: str = typer.Option("beep", "--backend", "-b", help="TTS backend: beep, gtts, or piper"),
    force: bool = typer.Option(False, "--force", "-f", help="Force rebuild existing clips"),
) -> None:
    """Pregenerate audio clips for all message templates."""
    typer.echo(f"Building audio clips using backend '{backend}' into '{output_dir}'...")
    manifest = build_all_clips(output_dir=output_dir, backend=backend, force=force)
    typer.echo(f"Successfully generated/verified {manifest.get('total_clips', 0)} audio clips.")


@app.callback()
def main() -> None:
    """AirCue: Event-driven outdoor school voice alert system."""
    pass


if __name__ == "__main__":
    app()
