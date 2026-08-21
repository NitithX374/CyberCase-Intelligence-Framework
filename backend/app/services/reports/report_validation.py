from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel

from app.config import settings
from app.schemas.reports import (
    REPORT_SECTION_HEADINGS_BY_VERSION,
    REPORT_SECTION_IDS_BY_VERSION,
    StructuredReport,
)
from app.services.reports.report_contracts import (
    INCIDENT_PROSE_RE,
    MITRE_ID_RE,
    MITRE_PROSE_RE,
    REPORT_STATUS,
    SECRET_RE,
    ReportValidationError,
)

def validate_structured_report(
    value: object,
    *,
    incident_ids: set[str],
    mitre_ids: set[str],
    evidence_ids: set[str] | None = None,
    timeline_ids: set[str] | None = None,
) -> StructuredReport:
    """Validate structure, exact sections, provenance references, and prose."""

    report = (
        value
        if isinstance(value, StructuredReport)
        else StructuredReport.model_validate(value)
    )
    if report.status != REPORT_STATUS:
        raise ReportValidationError("report status is not provisional_unverified")

    required_section_ids = REPORT_SECTION_IDS_BY_VERSION.get(report.report_version)
    required_headings = REPORT_SECTION_HEADINGS_BY_VERSION.get(report.report_version)
    if required_section_ids is None or required_headings is None:
        raise ReportValidationError("report version is not supported")

    section_ids = [section.section_id for section in report.sections]
    if tuple(section_ids) != required_section_ids:
        raise ReportValidationError("report sections do not match the required set")
    if len(set(section_ids)) != len(section_ids):
        raise ReportValidationError("report sections must be unique")

    claim_ids: set[str] = set()
    all_text: list[str] = [report.title, *report.limitations]
    for section in report.sections:
        if section.heading != required_headings[section.section_id]:
            raise ReportValidationError(
                f"section heading does not match {section.section_id}"
            )
        if not section.paragraphs and not section.items:
            raise ReportValidationError(
                f"section {section.section_id} must contain report content"
            )
        all_text.extend(section.paragraphs)
        all_text.extend(section.items)

    for claim in report.claims:
        all_text.append(claim.text)
        if claim.claim_id in claim_ids:
            raise ReportValidationError("claim IDs must be unique")
        claim_ids.add(claim.claim_id)
        if claim.section_id not in section_ids:
            raise ReportValidationError("claim references an unknown section")
        if len(set(claim.evidence_ids)) != len(claim.evidence_ids):
            raise ReportValidationError("claim evidence references must be unique")
        if len(set(claim.timeline_event_ids)) != len(claim.timeline_event_ids):
            raise ReportValidationError(
                "claim timeline references must be unique"
            )
        if len(set(claim.mitre_technique_ids)) != len(claim.mitre_technique_ids):
            raise ReportValidationError("claim MITRE references must be unique")

        admitted_evidence_ids = (
            incident_ids if evidence_ids is None else evidence_ids
        )
        admitted_timeline_ids = (
            incident_ids if timeline_ids is None else timeline_ids
        )
        if not set(claim.evidence_ids) <= admitted_evidence_ids:
            raise ReportValidationError("claim contains an unknown incident ID")
        if not set(claim.timeline_event_ids) <= admitted_timeline_ids:
            raise ReportValidationError("claim contains an unknown incident ID")
        if not set(claim.mitre_technique_ids) <= mitre_ids:
            raise ReportValidationError("claim contains an unknown MITRE ID")
        if any(not MITRE_ID_RE.fullmatch(ref) for ref in claim.mitre_technique_ids):
            raise ReportValidationError("claim contains an invalid MITRE ID")

        incident_refs = set(claim.evidence_ids) | set(claim.timeline_event_ids)
        if claim.support_type in {"user_reported", "extraction_candidate"}:
            if not incident_refs or claim.mitre_technique_ids:
                raise ReportValidationError(
                    "incident claims require only valid evidence/timeline references"
                )
        elif claim.support_type == "mitre_mapping_candidate":
            if not incident_refs or not claim.mitre_technique_ids:
                raise ReportValidationError(
                    "MITRE claims require admitted MITRE and incident references"
                )
        elif claim.support_type in {
            "general_technical_knowledge",
            "unknown",
        } and (incident_refs or claim.mitre_technique_ids):
            raise ReportValidationError(
                "general or unknown claims cannot contain incident references"
            )

        prose_incident_ids = {
            match.group(0) for match in INCIDENT_PROSE_RE.finditer(claim.text)
        }
        prose_mitre_ids = {
            match.group(0) for match in MITRE_PROSE_RE.finditer(claim.text)
        }
        if not prose_incident_ids <= incident_refs:
            raise ReportValidationError(
                "claim prose contains an unreferenced incident ID"
            )
        if not prose_mitre_ids <= set(claim.mitre_technique_ids):
            raise ReportValidationError("claim prose contains an unreferenced MITRE ID")

    max_text_chars = max(1, settings.chat_report_max_text_chars)
    if any(len(text) > max_text_chars for text in all_text):
        raise ReportValidationError("report text exceeds the configured limit")
    if any(not text.strip() for text in all_text):
        raise ReportValidationError("report text cannot be empty")
    for text in all_text:
        if _contains_secret_or_prompt_text(text):
            raise ReportValidationError("report contains secret or system-prompt text")
        if _contains_unsupported_prose_ids(
            text,
            incident_refs=incident_ids,
            mitre_refs=mitre_ids,
        ):
            raise ReportValidationError(
                "report prose contains an unsupported evidence, timeline, or MITRE ID"
            )

    if len(report.claims) > max(0, settings.chat_report_max_claims):
        raise ReportValidationError("report claims exceed the configured limit")
    if len(report.limitations) > max(0, settings.chat_report_max_limitations):
        raise ReportValidationError(
            "report limitations exceed the configured limit"
        )
    return report

def source_snapshot_hash(snapshot: ReportInputSnapshot | dict[str, object]) -> str:
    """Hash the canonical server-built report input snapshot."""

    payload = (
        snapshot.model_dump(mode="json")
        if isinstance(snapshot, BaseModel)
        else snapshot
    )
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _contains_unsupported_prose_ids(
    text: str,
    *,
    incident_refs: set[str],
    mitre_refs: set[str],
) -> bool:
    return any(
        match.group(0) not in incident_refs
        for match in INCIDENT_PROSE_RE.finditer(text)
    ) or any(
        match.group(0) not in mitre_refs for match in MITRE_PROSE_RE.finditer(text)
    )


def _contains_secret_or_prompt_text(value: str) -> bool:
    if SECRET_RE.search(value):
        return True
    normalized = " ".join(value.casefold().split())
    return any(
        marker in normalized
        for marker in (
            "prompt version: chat_report_prompt_v1",
            "prompt version: chat_report_prompt_v2",
            "you are the cybercase persisted digital-forensics report writer",
            "return json only",
            "system prompt",
        )
    )


def _validation_error_text(error: Exception) -> str:
    text = str(error).strip().replace("\n", " ")
    return text[:500] or "report output failed validation"


validation_error_text = _validation_error_text
