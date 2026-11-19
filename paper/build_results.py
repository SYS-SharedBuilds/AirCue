"""Build paper results macros and LaTeX snippets from latest benchmark results."""
from __future__ import annotations

import json
from pathlib import Path

from aircue.benchmark.metrics import compute_metrics
from aircue.data.store import load_latest_snapshot


def build_paper_results() -> None:
    """Read results and emit LaTeX macros file."""
    raw_path = Path("results/raw/latest_run.jsonl")
    macro_out = Path("paper/results_macros.tex")

    snapshot = load_latest_snapshot()
    total_rows = len(snapshot)
    num_locations = snapshot["location"].nunique()
    start_date = str(snapshot["timestamp"].min())[:10]
    end_date = str(snapshot["timestamp"].max())[:10]

    with open(macro_out, "w", encoding="utf-8") as f:
        f.write(f"\\newcommand{{\\datasetRows}}{{{total_rows:,}}}\n")
        f.write(f"\\newcommand{{\\datasetLocations}}{{{num_locations}}}\n")
        f.write(f"\\newcommand{{\\datasetStartDate}}{{{start_date}}}\n")
        f.write(f"\\newcommand{{\\datasetEndDate}}{{{end_date}}}\n")

        if not raw_path.exists():
            f.write("\\newcommand{\\benchmarkStatus}{RESULTS PENDING}\n")
            f.write("\\newcommand{\\isMockResults}{true}\n")
            return

        raw_results = []
        with open(raw_path, "r", encoding="utf-8") as rf:
            for line in rf:
                if line.strip():
                    raw_results.append(json.loads(line))

        metrics = compute_metrics(raw_results)
        is_mock = any("mock" in m for m in metrics.keys())

        f.write(f"\\newcommand{{\\benchmarkStatus}}{{'PROCESSED ({'MOCK' if is_mock else 'LIVE'})'}}\n")
        f.write(f"\\newcommand{{\\isMockResults}}{{{'true' if is_mock else 'false'}}}\n")
        f.write(f"\\newcommand{{\\totalEvaluatedModels}}{{{len(metrics)}}}\n")

    print(f"Paper macros written to {macro_out}")


if __name__ == "__main__":
    build_paper_results()
