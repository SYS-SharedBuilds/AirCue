"""AirCue CLI entrypoint."""
import typer
from aircue.audio.clips import build_all_clips

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
