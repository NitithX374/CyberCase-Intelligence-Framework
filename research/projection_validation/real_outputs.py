from __future__ import annotations

from collections import Counter
from dataclasses import asdict

from app.sources.bundle import CaseSourceItem
from app.sources.evidence import evidence_units

from research.projection_validation.runtime import (
    ROOT,
    file_digest,
    read_json,
    read_rows,
)

KINDS = ("involved_parties", "timeline", "impacts")
EN_RUN = "research/analysis_baseline/results/raw_main_20261001_021428"
TH_RUN = "evaluation/ocr_downstream/thaisum_ocr/results/raw_20261001_223057"
LABELS = {
    "10004": ("SAN N".replace(" ", ""), "ASNN", "SSS"),
    "10016": ("SSSA", "SA", "SSS"),
    "10018": ("SSNAAA", "S", "SSS"),
    "r100711": ("SNNNNNNNNN", "SA", "SN"),
    "r103688": ("SSSSA", "ASA", "SS"),
    "r107909": ("SNNNNAAA", "SA", "NN"),
}
RATIONALES = {
    "10004": {
        "N": "The linked claim omits this entity/access fact, or the projection narrows October 30 OR 31 to one asserted date.",
        "A": "Program/member metonymy or an Unknown time/event representation needs adjudication.",
    },
    "10016": {
        "A": "Data-subject terminology or the deadline anchor requires interpretation beyond explicit linked wording.",
    },
    "10018": {
        "N": "The linked staff-discovery claim names neither Rachel Williams nor her principal role.",
        "A": "Organizations are projected as individual forensics experts; metonymy is ambiguous.",
    },
    "r100711": {
        "N": "A generic group of officials does not establish the named official/role; a prison reorganization plan does not establish overcrowding.",
        "A": "The projection drops future modality and adds a relative announcement anchor.",
    },
    "r103688": {
        "A": "Relative dates or omitted institutional quantifiers require context/adjudication.",
    },
    "r107909": {
        "N": "Committee membership does not establish the occupational role; an award-winning headline does not entail the projected social impact.",
        "A": "University/newspaper award metonymy or a future planned award needs adjudication.",
    },
}


def saved_cases() -> list[dict]:
    en_data = ROOT / "research/analysis_baseline/data/cases.jsonl"
    th_data = ROOT / "evaluation/ocr_downstream/thaisum_ocr/data/articles.jsonl"
    articles = {
        **{row["id"]: row["text"] for row in read_rows(en_data)},
        **{row["id"]: row["clean"] for row in read_rows(th_data)},
    }
    output = []
    for key, codes in LABELS.items():
        thai = key.startswith("r")
        path = (
            ROOT
            / (TH_RUN if thai else EN_RUN)
            / (f"{key}_clean.json" if thai else f"{key}_cybercase_nogrammar_1.json")
        )
        saved = read_json(path)
        original = saved.get("reading") or saved["written"]
        grounded = saved["bound"]
        source = CaseSourceItem("SRC-1", "narrative", articles[key])
        claims, remapping = remapped_claims(grounded["claims"], source)
        reading = {"version": "case_analysis_trace_v1", "claims": claims}
        annotations = []
        for kind, labels in zip(KINDS, codes, strict=True):
            rows = original[kind]
            assert len(labels) == len(rows), (key, kind, labels, len(rows))
            reading[kind] = [
                {
                    field: value
                    for field, value in row.items()
                    if field not in {"support", "projection_grounding"}
                }
                for row in rows
            ]
            for index, label in enumerate(labels):
                annotations.append(
                    {
                        "projection_id": f"real-{key}:{kind}:{index}",
                        "type": kind,
                        "index": index,
                        "gold": {
                            "S": "supported",
                            "N": "not_supported",
                            "A": "ambiguous",
                        }[label],
                        "rationale": (
                            "All factual content is explicitly represented by the supplied linked claims."
                            if label == "S"
                            else RATIONALES[key][label]
                        ),
                        "perturbation": "original_saved_projection",
                        "error_scope": "unreviewed_source_to_claim",
                    }
                )
        output.append(
            {
                "case_id": f"real-{key}",
                "family_id": f"real-{key}",
                "origin": "saved_output",
                "language": "thai" if thai else "english",
                "sources": [asdict(source)],
                "reading": reading,
                "annotations": annotations,
                "provenance": {
                    "raw_path": path.relative_to(ROOT).as_posix(),
                    "raw_sha256": file_digest(path),
                    "dataset_path": (th_data if thai else en_data)
                    .relative_to(ROOT)
                    .as_posix(),
                    "dataset_sha256": file_digest(th_data if thai else en_data),
                    "citation_remapping": remapping,
                },
            }
        )
    return output


def remapped_claims(
    claims: list[dict], source: CaseSourceItem
) -> tuple[list[dict], dict]:
    units = evidence_units(source)
    output = []
    remapping = Counter()
    for claim in claims:
        new = {
            key: claim[key]
            for key in ("claim_id", "claim_type", "text", "epistemic_status")
        }
        for role in ("supporting_citations", "contradicting_citations"):
            selected = []
            for citation in claim.get(role, []):
                quote = citation["exact_quote"]
                start = source.text.find(quote)
                if citation["source_id"] != source.source_id or start < 0 or not quote:
                    remapping["not_exactly_remappable"] += 1
                    continue
                remapping["exactly_remapped"] += 1
                selected.extend(
                    unit.unit_id
                    for unit in units
                    if unit.start < start + len(quote) and unit.end > start
                )
            new[role] = (
                [
                    {
                        "source_id": source.source_id,
                        "evidence_unit_ids": list(dict.fromkeys(selected)),
                    }
                ]
                if selected
                else []
            )
        output.append(new)
    return output, dict(remapping)
