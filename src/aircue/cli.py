"""AirCue CLI entrypoint."""
import typer

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


@app.callback()
def main() -> None:
    """AirCue: Event-driven outdoor school voice alert system."""
    pass


if __name__ == "__main__":
    app()
