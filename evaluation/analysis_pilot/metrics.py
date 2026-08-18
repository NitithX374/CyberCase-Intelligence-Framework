"""Metric computations for Supported Probe Coverage, Epistemic Violations, and Factual Errors."""

from __future__ import annotations

from typing import Any
from evaluation.analysis_pilot.config import (
    EPISTEMIC_VIOLATION_TYPES,
    FACTUAL_ERROR_TYPES,
)
from evaluation.analysis_pilot.schemas import ProbeJudgmentRecord


def compute_case_metrics(
    judgments: list[ProbeJudgmentRecord],
) -> dict[str, Any]:
    """Compute supported probe coverage, epistemic violation rates, and factual error rates for a single case."""
    supported_total = 0
    supported_covered = 0

    epistemic_total = 0
    epistemic_violated = 0
    epistemic_by_type: dict[str, dict[str, int]] = {
        t: {"total": 0, "violated": 0} for t in EPISTEMIC_VIOLATION_TYPES
    }

    factual_total = 0
    factual_violated = 0
    factual_by_type: dict[str, dict[str, int]] = {
        t: {"total": 0, "violated": 0} for t in FACTUAL_ERROR_TYPES
    }

    for j in judgments:
        is_present = j.verdict == "PRESENT"

        if j.label == "SUPPORTED":
            supported_total += 1
            if is_present:
                supported_covered += 1

        elif j.label == "UNSUPPORTED":
            err_type = j.error_type
            if err_type in EPISTEMIC_VIOLATION_TYPES:
                epistemic_total += 1
                epistemic_by_type[err_type]["total"] += 1
                if is_present:
                    epistemic_violated += 1
                    epistemic_by_type[err_type]["violated"] += 1

            elif err_type in FACTUAL_ERROR_TYPES:
                factual_total += 1
                factual_by_type[err_type]["total"] += 1
                if is_present:
                    factual_violated += 1
                    factual_by_type[err_type]["violated"] += 1

    supported_coverage = (
        (supported_covered / supported_total) if supported_total > 0 else 0.0
    )
    epistemic_rate = (
        (epistemic_violated / epistemic_total) if epistemic_total > 0 else 0.0
    )
    factual_rate = (
        (factual_violated / factual_total) if factual_total > 0 else 0.0
    )

    return {
        "supported_probes_total": supported_total,
        "supported_probes_covered": supported_covered,
        "supported_probe_coverage": supported_coverage,
        "epistemic_probes_total": epistemic_total,
        "epistemic_probes_violated": epistemic_violated,
        "epistemic_probe_violation_rate": epistemic_rate,
        "epistemic_by_type": epistemic_by_type,
        "factual_probes_total": factual_total,
        "factual_probes_violated": factual_violated,
        "factual_error_probe_rate": factual_rate,
        "factual_by_type": factual_by_type,
    }


def compute_aggregate_metrics(
    case_metrics_list: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compute macro-averages and breakdown across all cases for a condition."""
    if not case_metrics_list:
        return {}

    n = len(case_metrics_list)
    macro_supported_coverage = sum(
        m["supported_probe_coverage"] for m in case_metrics_list
    ) / n

    # Filter cases that actually evaluated epistemic probes
    epistemic_cases = [
        m for m in case_metrics_list if m["epistemic_probes_total"] > 0
    ]
    macro_epistemic_rate = (
        sum(m["epistemic_probe_violation_rate"] for m in epistemic_cases)
        / len(epistemic_cases)
        if epistemic_cases
        else 0.0
    )

    # Filter cases that actually evaluated factual error probes
    factual_cases = [
        m for m in case_metrics_list if m["factual_probes_total"] > 0
    ]
    macro_factual_rate = (
        sum(m["factual_error_probe_rate"] for m in factual_cases)
        / len(factual_cases)
        if factual_cases
        else 0.0
    )

    # Breakdown by specific epistemic error types
    epistemic_breakdown: dict[str, dict[str, Any]] = {}
    for err_type in sorted(EPISTEMIC_VIOLATION_TYPES):
        tot = sum(
            m["epistemic_by_type"].get(err_type, {}).get("total", 0)
            for m in case_metrics_list
        )
        violated = sum(
            m["epistemic_by_type"].get(err_type, {}).get("violated", 0)
            for m in case_metrics_list
        )
        rate = (violated / tot) if tot > 0 else 0.0
        epistemic_breakdown[err_type] = {
            "total_probes": tot,
            "violations": violated,
            "rate": rate,
        }

    # Breakdown by specific factual error types
    factual_breakdown: dict[str, dict[str, Any]] = {}
    for err_type in sorted(FACTUAL_ERROR_TYPES):
        tot = sum(
            m["factual_by_type"].get(err_type, {}).get("total", 0)
            for m in case_metrics_list
        )
        violated = sum(
            m["factual_by_type"].get(err_type, {}).get("violated", 0)
            for m in case_metrics_list
        )
        rate = (violated / tot) if tot > 0 else 0.0
        factual_breakdown[err_type] = {
            "total_probes": tot,
            "violations": violated,
            "rate": rate,
        }

    return {
        "case_count": n,
        "macro_supported_probe_coverage": macro_supported_coverage,
        "macro_epistemic_probe_violation_rate": macro_epistemic_rate,
        "macro_factual_error_probe_rate": macro_factual_rate,
        "epistemic_breakdown": epistemic_breakdown,
        "factual_breakdown": factual_breakdown,
    }
