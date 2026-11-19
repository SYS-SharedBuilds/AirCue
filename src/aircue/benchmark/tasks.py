"""Benchmark tasks definition and evaluation execution."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from aircue.benchmark.quota import QuotaManager
from aircue.llm.base import LLMClient
from aircue.llm.parsing import parse_json_robust
from aircue.llm.prompts import (
    PROMPT_VERSION,
    SYSTEM_PROMPT_ANNOUNCEMENT,
    SYSTEM_PROMPT_DECISION,
    build_announcement_user_prompt,
    build_decision_user_prompt,
)
from aircue.llm.validators import validate_announcement


async def run_task1_generation(
    client: LLMClient,
    scenarios: List[Dict[str, Any]],
    quota: QuotaManager,
) -> List[Dict[str, Any]]:
    """Execute Task 1: Spoken Announcement Generation Quality."""
    results = []
    for sc in scenarios:
        if not quota.can_call():
            break

        prompt = build_announcement_user_prompt(sc)
        res = await client.complete(prompt=prompt, system_prompt=SYSTEM_PROMPT_ANNOUNCEMENT)
        quota.record_call(tokens=res.input_tokens + res.output_tokens)

        # Validate generated text
        val = validate_announcement(res.text, expected_lang=sc["language"], input_facts=sc)

        results.append({
            "task": "task1_generation",
            "scenario_id": sc["scenario_id"],
            "model": client.model,
            "prompt_version": PROMPT_VERSION,
            "level": sc["level"],
            "language": sc["language"],
            "tone": sc["tone"],
            "slot": sc["activity_slot"],
            "generated_text": res.text,
            "passed_all_rules": val.passed,
            "rule_results": val.rule_results,
            "failure_reasons": val.failure_reasons,
            "latency_s": res.latency_s,
            "input_tokens": res.input_tokens,
            "output_tokens": res.output_tokens,
            "cost_usd": res.cost_usd,
            "raw_error": res.raw_error,
        })
    return results


async def run_task2_decision(
    client: LLMClient,
    scenarios: List[Dict[str, Any]],
    quota: QuotaManager,
) -> List[Dict[str, Any]]:
    """Execute Task 2: Trigger Decision vs Ground Truth State Machine."""
    results = []
    for sc in scenarios:
        if not quota.can_call():
            break

        prompt = build_decision_user_prompt(sc["window"])
        res = await client.complete(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_DECISION,
            temperature=0.0,
        )
        quota.record_call(tokens=res.input_tokens + res.output_tokens)

        # Parse JSON
        parsed = parse_json_robust(res.text)
        is_parseable = parsed is not None

        pred_speak = parsed.get("speak") if is_parseable else None
        pred_level = parsed.get("level") if is_parseable else None

        gt = sc["ground_truth"]
        correct_speak = (pred_speak == gt["speak"]) if is_parseable else False
        correct_level = (pred_level == gt["level"]) if is_parseable else False

        results.append({
            "task": "task2_decision",
            "scenario_id": sc["scenario_id"],
            "model": client.model,
            "prompt_version": PROMPT_VERSION,
            "raw_output": res.text,
            "is_parseable": is_parseable,
            "pred_speak": pred_speak,
            "gt_speak": gt["speak"],
            "pred_level": pred_level,
            "gt_level": gt["level"],
            "correct_speak": correct_speak,
            "correct_level": correct_level,
            "latency_s": res.latency_s,
            "input_tokens": res.input_tokens,
            "output_tokens": res.output_tokens,
            "cost_usd": res.cost_usd,
            "raw_error": res.raw_error,
        })
    return results
