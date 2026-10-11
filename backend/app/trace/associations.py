from __future__ import annotations

from collections.abc import Mapping

from app.trace.trace import CaseMitreAssociation

MAX_ASSOCIATIONS = 64
MEANING_CHARS = 600
REASON_CHARS = 4_000


def reread_spans(row: Mapping[str, object]) -> list[tuple[int, str]]:
    evidence = row.get("evidence")
    if not isinstance(evidence, list):
        return []
    return sorted(
        {
            (span["start"], span["text"].strip())
            for span in evidence
            if isinstance(span, Mapping)
            and span.get("basis") == "reread"
            and isinstance(span.get("start"), int)
            and isinstance(span.get("text"), str)
            and span["text"].strip()
        }
    )


def first_sentence(text: object) -> str:
    words = " ".join(str(text or "").split())
    stop = words.find(". ")
    return (words[: stop + 1] if stop != -1 else words)[:MEANING_CHARS]


def mapped_associations(mitre_table: object) -> list[CaseMitreAssociation]:
    if not isinstance(mitre_table, (list, tuple)):
        return []
    rows: dict[str, tuple[int, str, str]] = {}
    for row in mitre_table:
        if not isinstance(row, Mapping):
            continue
        technique_id = str(row.get("technique_id") or "").strip()
        spans = reread_spans(row)
        if technique_id and spans and technique_id not in rows:
            reason = " ".join(f"“{text}”" for _, text in spans)
            rows[technique_id] = (spans[0][0], reason, first_sentence(row.get("description")))
    ordered = sorted((start, technique_id) for technique_id, (start, _, _) in rows.items())
    return [
        CaseMitreAssociation(
            association_id=f"MA-{number:02d}",
            technique_id=technique_id,
            claim_ids=[],
            reason=rows[technique_id][1][:REASON_CHARS],
            plain_meaning=rows[technique_id][2],
            status="candidate_only",
            support_role="external_technical_context",
        )
        for number, (_, technique_id) in enumerate(ordered[:MAX_ASSOCIATIONS], 1)
    ]


__all__ = ["mapped_associations"]
