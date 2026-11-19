"""Statistical metrics, confusion matrix, and performance aggregation."""
from __future__ import annotations

from typing import Any, Dict, List
import numpy as np


def compute_metrics(raw_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute aggregate statistical performance metrics per model and task."""
    models = sorted(list({r["model"] for r in raw_results}))
    summary: Dict[str, Any] = {}

    for m in models:
        m_results = [r for r in raw_results if r["model"] == m]
        t1_rows = [r for r in m_results if r.get("task") == "task1_generation"]
        t2_rows = [r for r in m_results if r.get("task") == "task2_decision"]

        m_summary: Dict[str, Any] = {}

        # Task 1 Metrics
        if t1_rows:
            n_t1 = len(t1_rows)
            pass_count = sum(1 for r in t1_rows if r.get("passed_all_rules"))
            latencies = [r.get("latency_s", 0.0) for r in t1_rows]

            # Rule violation breakdown
            violations: Dict[str, int] = {}
            for r in t1_rows:
                for reason in r.get("failure_reasons", []):
                    violations[reason] = violations.get(reason, 0) + 1

            m_summary["task1"] = {
                "total": n_t1,
                "overall_pass_rate": pass_count / n_t1 if n_t1 > 0 else 0.0,
                "p50_latency_s": float(np.percentile(latencies, 50)) if latencies else 0.0,
                "p95_latency_s": float(np.percentile(latencies, 95)) if latencies else 0.0,
                "violations": violations,
            }

        # Task 2 Metrics
        if t2_rows:
            n_t2 = len(t2_rows)
            parse_count = sum(1 for r in t2_rows if r.get("is_parseable"))
            speak_correct = sum(1 for r in t2_rows if r.get("correct_speak"))
            level_correct = sum(1 for r in t2_rows if r.get("correct_level"))
            latencies2 = [r.get("latency_s", 0.0) for r in t2_rows]

            m_summary["task2"] = {
                "total": n_t2,
                "json_parse_rate": parse_count / n_t2 if n_t2 > 0 else 0.0,
                "speak_accuracy": speak_correct / n_t2 if n_t2 > 0 else 0.0,
                "level_accuracy": level_correct / n_t2 if n_t2 > 0 else 0.0,
                "p50_latency_s": float(np.percentile(latencies2, 50)) if latencies2 else 0.0,
                "p95_latency_s": float(np.percentile(latencies2, 95)) if latencies2 else 0.0,
            }

        # Task 3: Latency & Speaker Blocking Risk (< 2.0s budget)
        all_lats = [r.get("latency_s", 0.0) for r in m_results]
        blocking_risk = (
            sum(1 for l in all_lats if l > 2.0) / len(all_lats) if all_lats else 0.0
        )
        m_summary["task3_reliability"] = {
            "total_calls": len(m_results),
            "speaker_blocking_risk_pct": blocking_risk * 100.0,
            "overall_p95_latency_s": float(np.percentile(all_lats, 95)) if all_lats else 0.0,
            "total_cost_usd": sum(r.get("cost_usd", 0.0) for r in m_results),
        }

        summary[m] = m_summary

    return summary
