"""Benchmark runner orchestrating tasks, saving raw logs, and enforcing quota stops."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aircue.benchmark.metrics import compute_metrics
from aircue.benchmark.mock import MockClient
from aircue.benchmark.quota import QuotaManager
from aircue.benchmark.report import generate_benchmark_reports
from aircue.benchmark.scenarios import generate_task1_scenarios, generate_task2_scenarios
from aircue.benchmark.tasks import run_task1_generation, run_task2_decision
from aircue.data.store import load_latest_snapshot
from aircue.llm.base import LLMClient
from aircue.llm.openrouter import OpenRouterClient


async def run_benchmark_suite(
    use_mock: bool = True,
    limit: int | None = None,
    raw_log_path: str | Path = "results/raw/latest_run.jsonl",
) -> list[dict[str, Any]]:
    """Execute complete benchmark suite across resolved models and tasks."""
    raw_path = Path(raw_log_path)
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    snapshot_df = load_latest_snapshot()
    n_t1 = limit if limit is not None else 160
    n_t2 = limit if limit is not None else 100

    scenarios_t1 = generate_task1_scenarios(snapshot_df, n_samples=n_t1)
    scenarios_t2 = generate_task2_scenarios(snapshot_df, n_samples=n_t2)

    quota = QuotaManager()

    clients: list[LLMClient] = []
    if use_mock:
        clients = [
            MockClient(model="gemma-4-31b-it:mock", seed=1),
            MockClient(model="nemotron-3.5-lightning:mock", seed=2),
        ]
    else:
        # Load discovered models snapshot
        models_dir = Path("results/models")
        files = sorted(models_dir.glob("discovered_*.json"))
        if not files:
            raise FileNotFoundError("No discovered models snapshot found. Run 'aircue models discover' first.")
        with open(files[-1], "r", encoding="utf-8") as f:
            disc = json.load(f)
        for m in disc.get("models", []):
            clients.append(OpenRouterClient(model=m["id"]))

    all_raw_results: list[dict[str, Any]] = []

    for client in clients:
        # Task 1
        t1_res = await run_task1_generation(client, scenarios_t1, quota)
        all_raw_results.extend(t1_res)

        # Task 2
        t2_res = await run_task2_decision(client, scenarios_t2, quota)
        all_raw_results.extend(t2_res)

    # Append to raw results log
    with open(raw_path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in all_raw_results)

    # Compute metrics and generate reports
    metrics = compute_metrics(all_raw_results)
    generate_benchmark_reports(all_raw_results, metrics)

    return all_raw_results
