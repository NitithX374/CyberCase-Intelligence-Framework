from __future__ import annotations

from collections import Counter

from app.sources.bundle import (
    CaseSourceBundle,
    CaseSourceItem,
    build_document_source_context,
)
from app.sources.evidence import EvidenceIndex, evidence_revision, evidence_units
from app.trace.bind import resolve_claim
from app.trace.claims import CaseAnalysisClaim, CaseSourceCitation
from app.trace.evidence_binding import evidence_counts
from app.trace.quote_binding import QuoteSearch


def structural_evaluation() -> dict:
    sources = (
        CaseSourceItem(
            "S1", "document", "John sent an email.\nJane received it.", "D1", "a.txt"
        ),
        CaseSourceItem(
            "S2", "document", "เจนได้รับอีเมล\nบริษัทสูญเสียเงิน 25000 บาท", "D2", "b.txt"
        ),
        CaseSourceItem("QA-03", "followup_answer", "The transfer occurred at 13:00."),
        CaseSourceItem("EMPTY", "narrative", " \n\t"),
    )
    index = EvidenceIndex(sources)
    search = QuoteSearch(index.sources)
    context = build_document_source_context(CaseSourceBundle(1, sources))
    first, second = evidence_units(sources[0])
    foreign = evidence_units(sources[1])[0]
    qa = evidence_units(sources[2])[0]
    empty = evidence_units(sources[3])[0]

    def pointer(source: str, *ids: str) -> CaseSourceCitation:
        return CaseSourceCitation(
            source_id=source, evidence_unit_ids=list(ids), pointer_state="unresolved"
        )

    trials = [
        ("valid", [pointer("S1", first.unit_id)], []),
        ("multiple_units", [pointer("S1", first.unit_id, second.unit_id)], []),
        (
            "cross_document",
            [pointer("S1", first.unit_id), pointer("S2", foreign.unit_id)],
            [],
        ),
        ("followup", [pointer("QA-03", qa.unit_id)], []),
        ("unknown_source", [pointer("NO-SOURCE", first.unit_id)], ["unknown_source"]),
        (
            "unknown_unit",
            [pointer("S1", f"S1:U999-{evidence_revision(sources[0].text)}")],
            ["unknown_unit"],
        ),
        ("malformed", [pointer("S1", "U001")], ["malformed_id"]),
        (
            "zero_ordinal",
            [pointer("S1", f"S1:U000-{evidence_revision(sources[0].text)}")],
            ["malformed_id"],
        ),
        (
            "stale",
            [pointer("S1", f"S1:U001-{evidence_revision('Old text')}")],
            ["stale_id"],
        ),
        ("cross_source", [pointer("S1", foreign.unit_id)], ["cross_source"]),
        ("duplicate", [pointer("S1", first.unit_id, first.unit_id)], ["duplicate_id"]),
        ("empty", [pointer("EMPTY", empty.unit_id)], ["empty_unit"]),
        (
            "mixed_valid_invalid",
            [pointer("S1", first.unit_id, "wrong")],
            ["malformed_id"],
        ),
        ("no_reference", [], []),
        (
            "legacy_recovered_control",
            [CaseSourceCitation(source_id="S1", exact_quote="John sent an email.")],
            [],
        ),
        (
            "legacy_unresolved_control",
            [CaseSourceCitation(source_id="S1", exact_quote="The moon exploded.")],
            [],
        ),
    ]
    written, resolved, rows = [], [], []
    for number, (name, citations, expected) in enumerate(trials, 1):
        claim = CaseAnalysisClaim(
            claim_id=f"A-{number:02d}",
            claim_type="reported",
            epistemic_status="reported",
            text=f"Structural pointer trial {name}",
            supporting_citations=citations,
        )
        bound = resolve_claim(claim, index.sources, context, search, index)
        reasons = [item.reason for item in bound.invalid_evidence]
        assert reasons == expected, (name, reasons, expected)
        written.append(claim)
        resolved.append(bound)
        rows.append(
            {
                "trial": name,
                "claim": bound.model_dump(mode="json"),
                "expected": expected,
            }
        )
    counts = evidence_counts(written, resolved, index)
    duplicates = sum(
        item.reason == "duplicate_id"
        for claim in resolved
        for item in claim.invalid_evidence
    )
    direct = sum(
        c.pointer_state == "direct"
        for claim in resolved
        for c in claim.supporting_citations
    )
    recovered = sum(
        c.pointer_state == "recovered"
        for claim in resolved
        for c in claim.supporting_citations
    )
    legacy_unresolved = sum(
        not claim.supporting_citations
        for claim, trial in zip(resolved, trials, strict=True)
        if trial[0] == "legacy_unresolved_control"
    )
    segmentation = []
    texts = (
        "First sentence. Second sentence!",
        "ภาษาไทย\nบรรทัดที่สอง",
        "INVOICE 1O0\n• 2S,000\n|row|v|",
        " \n\t",
        "",
        "🙂e\u0301\nX",
    )
    for number, text in enumerate(texts):
        source = CaseSourceItem(f"SEG-{number}", "narrative", text)
        units = evidence_units(source)
        exact = "".join(unit.text for unit in units) == text
        invariant = all(unit.text == text[unit.start : unit.end] for unit in units)
        stable = units == evidence_units(source)
        assert exact and invariant and stable
        segmentation.append(
            {
                "text": text,
                "units": len(units),
                "exact_reconstruction": exact,
                "offset_invariant": invariant,
                "stable": stable,
            }
        )
    local_collision_free = first.unit_id != foreign.unit_id
    assert local_collision_free
    return {
        "scope": "Controlled structural diagnostics, not a natural invalid-ID prevalence estimate.",
        "counts": counts,
        "invalid_id_rate": counts["evidence_ids_invalid"]
        / counts["evidence_ids_claimed"],
        "duplicate_reference_rate": duplicates / counts["evidence_ids_claimed"],
        "claims_with_resolved_evidence": sum(
            bool(claim.supporting_citations) for claim in resolved
        ),
        "claims_without_resolved_evidence": sum(
            not claim.supporting_citations for claim in resolved
        ),
        "pointer_distribution": {
            "direct": direct,
            "recovered": recovered,
            "unresolved": counts["evidence_ids_invalid"] + legacy_unresolved,
        },
        "invalid_reasons": dict(
            Counter(
                item.reason for claim in resolved for item in claim.invalid_evidence
            )
        ),
        "local_collision_free": local_collision_free,
        "segmentation": segmentation,
        "trials": rows,
    }
