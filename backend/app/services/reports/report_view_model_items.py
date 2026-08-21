from __future__ import annotations;

from dataclasses import dataclass

from app.schemas.reports import ReportSection
from app.services.reports.report_view_model_contracts import (
    EvidenceViewRow,
    IndicatorViewRow,
    RelationshipViewRow,
    ReportLanguage,
    TimelineViewRow,
)
from app.services.reports.report_view_model_text import (
    _extract_indicators_from_text,
    _strict_marked_fields,
)


@dataclass(frozen=True)
class ParsedReportItems:
    evidence_rows: list[EvidenceViewRow]
    indicator_rows: list[IndicatorViewRow]
    timeline_rows: list[TimelineViewRow]
    relationship_rows: list[RelationshipViewRow]
    has_indicators: bool
    has_relationships: bool


def parse_report_items(
    sections_by_id: dict[str, ReportSection],
    *,
    language: ReportLanguage,
    relationship_templates: dict[str, str],
) -> ParsedReportItems:
    evidence_rows: list[EvidenceViewRow] = []
    seen_iocs: set[str] = set()
    indicator_rows: list[IndicatorViewRow] = []

    raw_evidence_items = []
    for sec_id in ("evidence_findings", "indicators_found"):
        if sec_id in sections_by_id:
            raw_evidence_items.extend(sections_by_id[sec_id].items)

    for item in raw_evidence_items:
        parsed = _strict_marked_fields(
            item,
            (
                " | Title: ",
                " | Description: ",
                " | Artifact type: ",
                " | Status: ",
                " | Confidence: ",
                " | Source type: ",
            ),
            terminal_period=True,
        )
        if parsed is not None:
            ev_id, ev_title, ev_desc, art_type, ev_status, ev_conf, src_type = parsed
            evidence_rows.append(
                EvidenceViewRow(
                    item_id=ev_id,
                    title=ev_title,
                    artifact_type=art_type,
                    description=ev_desc,
                    source_type=src_type,
                    confidence=ev_conf,
                )
            )
            note_text = (
                f"Observed in {ev_id} ({ev_title})"
                if language == "en"
                else f"พบในหลักฐาน {ev_id} ({ev_title})"
            )
            iocs = _extract_indicators_from_text(
                f"{ev_title} {ev_desc}",
                note=note_text,
                seen=seen_iocs,
            )
            indicator_rows.extend(iocs)
        elif "No evidence" not in item:
            evidence_rows.append(
                EvidenceViewRow(
                    item_id="-",
                    title=item,
                    artifact_type="Note" if language == "en" else "บันทึกข้อความ",
                    description=item,
                    source_type="User Reported" if language == "en" else "รายงานผู้ใช้",
                    confidence="candidate",
                )
            )

    timeline_rows: list[TimelineViewRow] = []
    relationship_rows: list[RelationshipViewRow] = []
    entity_name_map: dict[str, str] = {}

    raw_examine_items = []
    for sec_id in ("chronological_timeline", "individuals_accounts_systems_roles", "evidence_to_examine"):
        if sec_id in sections_by_id:
            raw_examine_items.extend(sections_by_id[sec_id].items)

    timeline_order = 1
    for item in raw_examine_items:
        tl_parsed = _strict_marked_fields(
            item,
            (
                " | Time: ",
                " | Event: ",
                " | Actors: ",
                " | Linked evidence: ",
                " | Status: ",
                " | Confidence: ",
            ),
            terminal_period=True,
        )
        if tl_parsed is not None:
            tl_id, tl_time, tl_event, tl_actors, tl_ev, tl_status, tl_conf = tl_parsed
            timeline_rows.append(
                TimelineViewRow(
                    order=timeline_order,
                    time_display=tl_time,
                    event=tl_event,
                    source_evidence=f"{tl_ev} ({tl_id})",
                    actors=tl_actors if tl_actors != "none persisted" else "-",
                    status=tl_status,
                )
            )
            timeline_order += 1
            continue

        ent_parsed = _strict_marked_fields(
            item,
            (
                "Entity | Name: ",
                " | Type: ",
                " | Reported role: ",
                " | Persisted status: ",
                " | Confidence: ",
            ),
            terminal_period=True,
            leading_empty=True,
        )
        if ent_parsed is not None:
            name, e_type, role, p_status, conf = ent_parsed
            entity_name_map[name] = name
            if e_type in {"ip", "domain", "url", "hash", "file", "host", "account"}:
                if name not in seen_iocs:
                    seen_iocs.add(name)
                    indicator_rows.append(
                        IndicatorViewRow(
                            indicator_type=e_type.upper(),
                            value=name,
                            note=(
                                f"Role: {role}"
                                if language == "en"
                                else f"ระบุในบทบาท: {role}"
                            ),
                        )
                    )
            continue

        if item.startswith("Relationship | "):
            rel_content = item[len("Relationship | ") :]
            rel_parsed = _strict_marked_fields(
                rel_content,
                (
                    " | Statement: ",
                    " | Status: ",
                    " | Confidence: ",
                ),
                terminal_period=True,
            )
            if rel_parsed is not None:
                rel_triplet, statement, status, conf = rel_parsed
                if rel_triplet.count(" -> ") == 2:
                    sub, pred, obj = rel_triplet.split(" -> ")
                    pred_clean = pred.strip().lower()
                    if pred_clean in relationship_templates:
                        stmt_display = relationship_templates[pred_clean].format(subject=sub, object=obj)
                    elif statement.strip():
                        stmt_display = statement.strip()
                    else:
                        stmt_display = f"{sub} -> {pred} -> {obj}"
                    relationship_rows.append(
                        RelationshipViewRow(
                            statement=stmt_display,
                            subject_name=sub,
                            predicate=pred,
                            object_name=obj,
                            status=status,
                            confidence=conf,
                        )
                    )
                    continue

        if "chronological_timeline" in sections_by_id and item in sections_by_id["chronological_timeline"].items:
            if "No timeline" not in item:
                timeline_rows.append(
                    TimelineViewRow(
                        order=timeline_order,
                        time_display="Unspecified" if language == "en" else "ไม่ระบุเวลา",
                        event=item,
                        source_evidence="User Reported" if language == "en" else "รายงานผู้ใช้",
                        actors="-",
                        status="reported",
                    )
                )
                timeline_order += 1

    has_indicators = len(indicator_rows) > 0
    has_relationships = len(relationship_rows) > 0



    return ParsedReportItems(
        evidence_rows=evidence_rows,
        indicator_rows=indicator_rows,
        timeline_rows=timeline_rows,
        relationship_rows=relationship_rows,
        has_indicators=has_indicators,
        has_relationships=has_relationships,
    )
