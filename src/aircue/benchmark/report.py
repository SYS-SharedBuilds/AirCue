"""Benchmark report generation: Markdown summaries, CSV tables, LaTeX booktabs, and figures."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
import matplotlib.pyplot as plt
import pandas as pd


def generate_benchmark_reports(
    raw_results: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    report_dir: str | Path = "results/report",
    tables_dir: str | Path = "paper/tables",
    figures_dir: str | Path = "paper/figures",
) -> None:
    """Generate all artifact formats from raw benchmark results."""
    rep_path = Path(report_dir)
    tbl_path = Path(tables_dir)
    fig_path = Path(figures_dir)
    rep_path.mkdir(parents=True, exist_ok=True)
    tbl_path.mkdir(parents=True, exist_ok=True)
    fig_path.mkdir(parents=True, exist_ok=True)

    # 1. Generate Markdown Summary
    summary_md = rep_path / "summary.md"
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write("# AirCue Benchmark Evaluation Summary\n\n")
        f.write("| Model | Task 1 Pass Rate | Task 2 Speak Acc | Task 2 Level Acc | p95 Latency (s) | Blocking Risk (>2s) |\n")
        f.write("|---|---|---|---|---|---|\n")
        for m, d in metrics.items():
            t1 = d.get("task1", {})
            t2 = d.get("task2", {})
            rel = d.get("task3_reliability", {})
            f.write(
                f"| `{m}` | {t1.get('overall_pass_rate', 0.0):.1%} | "
                f"{t2.get('speak_accuracy', 0.0):.1%} | {t2.get('level_accuracy', 0.0):.1%} | "
                f"{rel.get('overall_p95_latency_s', 0.0):.2f}s | {rel.get('speaker_blocking_risk_pct', 0.0):.1f}% |\n"
            )

    # 2. LaTeX Tables (booktabs format)
    latex_tbl = tbl_path / "benchmark_summary.tex"
    with open(latex_tbl, "w", encoding="utf-8") as f:
        f.write("\\begin{table}[htbp]\n\\centering\n\\small\n")
        f.write("\\caption{Benchmark Performance of Open-Weight Models on AirCue Tasks}\n")
        f.write("\\label{tab:benchmark_summary}\n")
        f.write("\\begin{tabular}{lccccc}\n\\toprule\n")
        f.write("\\textbf{Model} & \\textbf{T1 Pass} & \\textbf{T2 Speak Acc} & \\textbf{T2 Level Acc} & \\textbf{p95 Latency} & \\textbf{Block Risk} \\\\\n\\midrule\n")
        for m, d in metrics.items():
            clean_name = m.replace("_", "\\_").replace("/", "/\\allowbreak ")
            t1 = d.get("task1", {})
            t2 = d.get("task2", {})
            rel = d.get("task3_reliability", {})
            t1_pct = t1.get("overall_pass_rate", 0.0) * 100.0
            t2_speak_pct = t2.get("speak_accuracy", 0.0) * 100.0
            t2_lvl_pct = t2.get("level_accuracy", 0.0) * 100.0
            f.write(
                f"{clean_name} & {t1_pct:.1f}\\% & "
                f"{t2_speak_pct:.1f}\\% & {t2_lvl_pct:.1f}\\% & "
                f"{rel.get('overall_p95_latency_s', 0.0):.2f}s & {rel.get('speaker_blocking_risk_pct', 0.0):.1f}\\% \\\\\n"
            )
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    # 3. Matplotlib Figure: Pass Rate vs Speaker Latency
    if metrics:
        models = list(metrics.keys())
        pass_rates = [metrics[m].get("task1", {}).get("overall_pass_rate", 0.0) * 100.0 for m in models]
        latencies = [metrics[m].get("task3_reliability", {}).get("overall_p95_latency_s", 0.0) for m in models]

        plt.figure(figsize=(7, 4))
        plt.bar(range(len(models)), pass_rates, color="#2b5c8f", alpha=0.85)
        plt.xticks(range(len(models)), [m.split("/")[-1] for m in models], rotation=20, ha="right")
        plt.ylabel("Rule Pass Rate (%)")
        plt.title("Task 1 Announcement Quality Pass Rate by Model")
        plt.tight_layout()
        plt.savefig(fig_path / "model_pass_rates.png", dpi=300)
        plt.savefig(fig_path / "model_pass_rates.pdf")
        plt.close()
