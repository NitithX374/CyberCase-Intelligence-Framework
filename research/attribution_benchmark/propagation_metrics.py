from __future__ import annotations

import re

from app.trace.summary import SUMMARY_CLAIM_IDS, summary_pieces

from research.attribution_benchmark.propagation_data import ResponseCluster


def ratio(numerator: int, denominator: int) -> dict:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def labelled_ids(cluster: ResponseCluster) -> tuple[set[str], set[str]]:
    positive = {
        claim_id
        for claim_id, row in cluster.assigned_rows
        if row["attribution_label"] == "attributable"
    }
    negative = {
        claim_id
        for claim_id, row in cluster.assigned_rows
        if row["attribution_label"] == "not attributable"
    }
    return positive, negative


def admission_metrics(cluster: ResponseCluster, accepted: set[str]) -> dict:
    positive, negative = labelled_ids(cluster)
    if not accepted <= positive | negative:
        raise ValueError("Admission contains unknown claim IDs")
    return {
        "original_rows": len(cluster.rows),
        "accepted_rows": len(accepted),
        "non_attributable_admission": ratio(len(accepted & negative), len(negative)),
        "attributable_admission_retention": ratio(len(accepted & positive), len(positive)),
    }


def propagation_metrics(cluster: ResponseCluster, accepted: set[str], summary: str) -> dict:
    positive, negative = labelled_ids(cluster)
    admission_metrics(cluster, accepted)
    pieces = summary_pieces(summary)
    cited = {claim_id for _, ids in pieces for claim_id in ids}
    known = positive | negative
    rejected = (cited & known) - accepted
    unknown = cited - known
    malformed = re.findall(r"\[[^\]\n]*A-?\d[^\]\n]*\]", SUMMARY_CLAIM_IDS.sub("", summary))
    observed = cited & accepted
    return {
        "endpoint": "structural benchmark row ID citation; semantic factuality unassessed",
        "cited_accepted_claim_ids": sorted(observed),
        "cited_rejected_claim_ids": sorted(rejected),
        "unknown_claim_ids": sorted(unknown),
        "malformed_claim_brackets": malformed,
        "protocol_valid": bool(pieces)
        and not (rejected or unknown or malformed)
        and all(ids for _, ids in pieces),
        "citation_blocks": len(pieces),
        "uncited_blocks": sum(not ids for _, ids in pieces),
        "blocks_citing_non_attributable_accepted_rows": ratio(
            sum(bool(set(ids) & negative & accepted) for _, ids in pieces), len(pieces)
        ),
        "non_attributable_propagation": ratio(len(observed & negative), len(negative)),
        "non_attributable_citation_exposure_including_rejected": ratio(
            len(cited & negative), len(negative)
        ),
        "attributable_downstream_retention": ratio(len(observed & positive), len(positive)),
        "non_attributable_conditional_propagation": ratio(
            len(observed & negative), len(accepted & negative)
        ),
        "attributable_conditional_retention": ratio(
            len(observed & positive), len(accepted & positive)
        ),
    }
