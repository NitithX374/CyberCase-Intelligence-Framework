from __future__ import annotations

from dataclasses import asdict

from app.sources.bundle import CaseSourceItem
from app.sources.evidence import evidence_units

KINDS = ("involved_parties", "timeline", "impacts")


def materialize(spec: dict) -> dict:
    claims = spec["claims"]
    sources = [
        CaseSourceItem("S1", "document", "\n".join(claims[:2]), "D1", "statement.txt"),
        CaseSourceItem(
            "S2", "document", "\n".join(claims[2:]), "D2", "loss-record.txt"
        ),
    ]
    provider_claims = []
    for index, text in enumerate(claims):
        source = sources[0 if index < 2 else 1]
        start = source.text.index(text)
        selected = [
            unit.unit_id
            for unit in evidence_units(source)
            if unit.start < start + len(text) and unit.end > start
        ]
        provider_claims.append(
            {
                "claim_id": f"A-{index + 1:02d}",
                "claim_type": "reported",
                "text": text,
                "epistemic_status": "reported",
                "supporting_citations": [
                    {"source_id": source.source_id, "evidence_unit_ids": selected}
                ],
            }
        )
    reading = {"version": "case_analysis_trace_v1", "claims": provider_claims}
    annotations = []
    for kind in KINDS:
        variants = spec["projections"][kind]
        reading[kind] = [variant["item"] for variant in variants]
        for index, variant in enumerate(variants):
            annotations.append(
                {
                    "projection_id": f"{spec['case_id']}:{kind}:{index}",
                    "type": kind,
                    "index": index,
                    "gold": "supported" if index == 0 else "not_supported",
                    "rationale": variant["rationale"],
                    "perturbation": variant["perturbation"],
                    "error_scope": "none" if index == 0 else "projection_only",
                }
            )
    return {
        "case_id": spec["case_id"],
        "family_id": spec["family_id"],
        "origin": "controlled",
        "language": spec["language"],
        "sources": [asdict(source) for source in sources],
        "reading": reading,
        "annotations": annotations,
        "provenance": {"source": "independently authored controlled specification"},
    }


def projections(
    name: str,
    other: str,
    role: str,
    wrong_role: str,
    other_role: str,
    legal_role: str,
    time: str,
    wrong_time: str,
    event: str,
    wrong_event: str,
    other_event: str,
    causal_event: str,
    impact: str,
    bad_impacts: list[str],
) -> dict:
    def party(entity: str, value: str) -> dict:
        return {"name": entity, "role": value, "claim_ids": ["A-01"]}

    def timeline(moment: str, value: str) -> dict:
        return {"time": moment, "event": value, "claim_ids": ["A-02"]}

    def loss(value: str) -> dict:
        return {"description": value, "claim_ids": ["A-03"]}

    items = {
        "involved_parties": [
            (
                party(name, role),
                "explicit",
                "A-01 explicitly names the entity and role.",
            ),
            (party(name, wrong_role), "wrong_role", "A-01 does not assign this role."),
            (
                party(other, role),
                "wrong_name",
                "The named role belongs to another entity.",
            ),
            (
                party(name, legal_role),
                "legal_role",
                "No linked claim establishes this legal status.",
            ),
            (
                party(name, other_role),
                "borrowed_role",
                "A-04 assigns this role to another entity.",
            ),
        ],
        "timeline": [
            (
                timeline(time, event),
                "explicit",
                "A-02 explicitly states this complete time-event pair.",
            ),
            (
                timeline(wrong_time, event),
                "wrong_time",
                "The event is linked to a different time.",
            ),
            (
                timeline(time, wrong_event),
                "wrong_event",
                "The linked time belongs to a different event.",
            ),
            (
                timeline(time, other_event),
                "borrowed_event",
                "A-04's event is not established at A-02's time.",
            ),
            (
                timeline(time, causal_event),
                "invented_cause",
                "The linked claim states no such causal relation.",
            ),
        ],
        "impacts": [
            (loss(impact), "explicit", "A-03 explicitly states this complete impact."),
            *[
                (loss(value), perturbation, reason)
                for value, perturbation, reason in zip(
                    bad_impacts,
                    (
                        "wrong_amount",
                        "wrong_asset",
                        "unsupported_severity",
                        "borrowed_impact",
                    ),
                    (
                        "The amount or duration differs from the linked claim.",
                        "The affected entity or asset differs from the linked claim.",
                        "The added severity is absent from the linked claim.",
                        "This impact belongs to A-04 rather than the linked claim.",
                    ),
                    strict=True,
                )
            ],
        ],
    }
    return {
        kind: [
            {"item": item, "perturbation": perturbation, "rationale": reason}
            for item, perturbation, reason in variants
        ]
        for kind, variants in items.items()
    }
