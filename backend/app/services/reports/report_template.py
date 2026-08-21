from __future__ import annotations

from app.schemas.reports import (
    PRELIMINARY_REPORT_SECTION_HEADINGS,
    ReportClaim,
    ReportSection,
    StructuredReport,
)
from app.services.reports.report_contracts import (
    REPORT_STATUS,
    REPORT_VERSION,
    _TEMPLATE_CLAIM_LIMIT,
    _TEMPLATE_SECTION_ITEM_LIMIT,
    _TEMPLATE_TEXT_LIMIT,
    AdmittedMitreRow,
    ReportInputSnapshot,
)
from app.services.reports.report_template_content import build_investigation_evidence
from app.services.reports.report_validation import validate_structured_report

def build_template_report(snapshot: ReportInputSnapshot) -> StructuredReport:
    """Map one frozen snapshot to the ordered preliminary-analysis contract."""

    limitations = [
        (
            "This report is provisional and unverified; deterministic formatting "
            "does not establish that any incident statement is accurate."
        ),
        (
            "The system has not performed independent forensic verification of the "
            "original artifacts."
        ),
        (
            "MITRE ATT&CK rows are retrieval candidates only; the snapshot contains "
            "no explicit evidence-to-technique links or evidence-linked rationale."
        ),
    ]
    text_truncation_count = 0

    def bounded_text(value: object, *, limit: int = _TEMPLATE_TEXT_LIMIT) -> str:
        nonlocal text_truncation_count
        text = str(value).strip()
        if len(text) <= limit:
            return text
        text_truncation_count += 1
        omitted = len(text) - limit
        suffix = f" ... [truncated {omitted} characters]"
        return f"{text[: max(1, limit - len(suffix))].rstrip()}{suffix}"

    def record_omission(label: str, omitted: int) -> None:
        if omitted > 0:
            limitations.append(
                f"{label} omitted {omitted} item(s) after the stable report limit."
            )

    title = bounded_text(
        f"รายงานวิเคราะห์เบื้องต้น: {snapshot.thread_title}",
        limit=200,
    )
    included_messages = snapshot.source_messages[:_TEMPLATE_SECTION_ITEM_LIMIT]
    record_omission(
        "Source messages",
        len(snapshot.source_messages) - len(included_messages),
    )
    source_items = [
        bounded_text(
            f"Message {message.ordinal} ({message.source_type}): {message.content}"
        )
        for message in included_messages
    ] or ["No user-authored source messages were admitted for this snapshot."]

    included_evidence = snapshot.extraction.evidence[:_TEMPLATE_SECTION_ITEM_LIMIT]
    record_omission(
        "Evidence or indicator candidates",
        len(snapshot.extraction.evidence) - len(included_evidence),
    )
    indicator_items: list[str] = []
    claims: list[ReportClaim] = []
    for evidence in included_evidence:
        text = bounded_text(
            f"{evidence.evidence_id} | Title: {evidence.title} | Description: "
            f"{evidence.description} | Artifact type: {evidence.artifact_type} | "
            f"Status: {evidence.status} | Confidence: {evidence.confidence} | "
            f"Source type: {evidence.source_type}."
        )
        indicator_items.append(text)
        claims.append(
            ReportClaim(
                claim_id=f"C-{len(claims) + 1:03d}",
                section_id="indicators_found",
                text=text,
                support_type=(
                    "user_reported"
                    if evidence.status == "reported"
                    else "extraction_candidate"
                ),
                evidence_ids=[evidence.evidence_id],
            )
        )
    if not indicator_items:
        indicator_items = [
            "No evidence or indicator candidates were persisted for this snapshot."
        ]

    included_mitre_rows = snapshot.mitre_rows[:_TEMPLATE_SECTION_ITEM_LIMIT]
    record_omission(
        "MITRE ATT&CK mapping candidates",
        len(snapshot.mitre_rows) - len(included_mitre_rows),
    )
    mitre_items: list[str] = []
    rationale_items: list[str] = []
    for row in included_mitre_rows:
        score = "not reported" if row.score is None else format(row.score, ".12g")
        tactic = row.tactic or "not reported"
        entity_type = row.entity_type or "not reported"
        description = row.description or "No description was persisted."
        mitre_items.append(
            bounded_text(
                f"{row.technique_id} | Name: {row.name} | Mapping status: "
                f"candidate | Source: {row.source} | Relevance: {row.relevance} | "
                f"Score: {score} | Tactic: {tactic} | Entity type: {entity_type} | "
                f"Description: {description}"
            )
        )
        rationale_items.append(
            bounded_text(
                f"{row.technique_id} | Retrieval source: {row.source} | "
                f"Relevance: {row.relevance} | Score: {score} | Evidence link: none "
                "persisted | Rationale status: retrieval metadata only; no "
                "evidence-linked rationale was persisted."
            )
        )
    if not mitre_items:
        mitre_items = [
            "No MITRE ATT&CK mapping candidates were admitted for this snapshot."
        ]
        rationale_items = [
            "No mapping rationale is available because no MITRE ATT&CK mapping "
            "candidates were admitted for this snapshot."
        ]

    investigation = build_investigation_evidence(
        snapshot,
        bounded_text=bounded_text,
        record_omission=record_omission,
        claim_start=len(claims),
    )
    entities = investigation.entities
    relationships = investigation.relationships
    evidence_to_examine_items = investigation.items
    claims.extend(investigation.claims)

    recommendations = [
        (
            "Preserve original artifacts and forensic copies before analysis, and "
            "record handling details in the applicable chain-of-custody process."
        ),
        (
            "Verify every reported or candidate indicator against original artifacts "
            "before treating it as a confirmed finding."
        ),
        (
            "Normalize and corroborate timestamps, actors, and persisted evidence "
            "references before relying on the preliminary timeline."
        ),
        (
            "Validate each MITRE ATT&CK candidate independently; do not infer an "
            "incident-to-technique link from retrieval metadata alone."
        ),
    ]

    warnings = snapshot.extraction.warnings
    # Keep room for both omission and text-truncation disclosures.
    warning_capacity = max(
        0,
        _TEMPLATE_SECTION_ITEM_LIMIT - len(limitations) - 2,
    )
    if warnings:
        included_warnings = warnings[:warning_capacity]
        limitations.extend(
            bounded_text(f"Extraction warning: {warning}")
            for warning in included_warnings
        )
    else:
        included_warnings = []
        limitations.append("No extraction warnings were persisted for this snapshot.")
    record_omission("Extraction warnings", len(warnings) - len(included_warnings))

    if text_truncation_count:
        limitations.append(
            f"Template rendering truncated {text_truncation_count} text value(s) "
            "to stable report field bounds."
        )
    limitations = limitations[:_TEMPLATE_SECTION_ITEM_LIMIT]

    headings = PRELIMINARY_REPORT_SECTION_HEADINGS
    sections = [
        ReportSection(
            section_id="case_summary",
            heading=headings["case_summary"],
            paragraphs=[
                (
                    "This preliminary report is provisional and unverified. It "
                    "deterministically reassembles persisted case state and admitted "
                    "retrieval metadata without adding forensic conclusions."
                ),
                (
                    f"Snapshot scope: {len(snapshot.source_messages)} user-authored "
                    f"source message(s), {len(snapshot.extraction.evidence)} evidence "
                    f"or indicator candidate(s), {len(snapshot.extraction.timeline)} "
                    f"timeline event(s), {len(entities)} entity candidate(s), "
                    f"{len(relationships)} relationship candidate(s), and "
                    f"{len(snapshot.mitre_rows)} MITRE ATT&CK mapping candidate(s)."
                ),
            ],
            items=source_items,
        ),
        ReportSection(
            section_id="indicators_found",
            heading=headings["indicators_found"],
            paragraphs=[
                (
                    "Persisted status, confidence, source, and artifact fields are "
                    "reproduced without strengthening or confirmation."
                )
            ],
            items=indicator_items,
        ),
        ReportSection(
            section_id="mitre_attack_mapping",
            heading=headings["mitre_attack_mapping"],
            paragraphs=[
                (
                    "Rows are admitted retrieval results presented only as mapping "
                    "candidates; no evidence or timeline pairing is asserted."
                )
            ],
            items=mitre_items,
        ),
        ReportSection(
            section_id="mapping_rationale",
            heading=headings["mapping_rationale"],
            paragraphs=[
                (
                    "The available basis is limited to persisted retrieval source, "
                    "relevance, and score metadata. No evidence-linked rationale was "
                    "persisted."
                )
            ],
            items=rationale_items,
        ),
        ReportSection(
            section_id="evidence_to_examine",
            heading=headings["evidence_to_examine"],
            paragraphs=[
                (
                    "Timeline, entity, and relationship fields below are candidates "
                    "to verify against original artifacts; uncertainty is preserved."
                )
            ],
            items=evidence_to_examine_items,
        ),
        ReportSection(
            section_id="preliminary_recommendations",
            heading=headings["preliminary_recommendations"],
            paragraphs=[
                (
                    "These are generic preservation and verification procedures, not "
                    "incident-specific conclusions or remediation directives."
                )
            ],
            items=recommendations,
        ),
        ReportSection(
            section_id="system_limitations",
            heading=headings["system_limitations"],
            paragraphs=[
                (
                    "The limitations below define what this deterministic preliminary "
                    "report has not established."
                )
            ],
            items=list(limitations),
        ),
    ]

    report = StructuredReport(
        report_version=REPORT_VERSION,
        status=REPORT_STATUS,
        title=title,
        sections=sections,
        claims=claims[:_TEMPLATE_CLAIM_LIMIT],
        limitations=limitations,
    )
    evidence_ids = {item.evidence_id for item in snapshot.extraction.evidence}
    timeline_ids = {item.event_id for item in snapshot.extraction.timeline}
    return validate_structured_report(
        report,
        incident_ids=evidence_ids | timeline_ids,
        mitre_ids={row.technique_id for row in snapshot.mitre_rows},
        evidence_ids=evidence_ids,
        timeline_ids=timeline_ids,
    )
