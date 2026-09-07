import re

from app.schemas.reports import ReportSection
from app.services.reports.report_contracts import ReportInputSnapshot
from app.services.reports.report_view_model_contracts import (
    MitreMappingViewRow,
    ReportLanguage,
)
from app.services.reports.report_view_model_text import I18N_STRINGS


def project_mitre_rows(
    snapshot: ReportInputSnapshot | None,
    sections_by_id: dict[str, ReportSection],
    *,
    lang: ReportLanguage,
) -> list[MitreMappingViewRow]:
    i18n = I18N_STRINGS[lang]
    mitre_view_rows: list[MitreMappingViewRow] = []
    if snapshot and snapshot.mitre_rows:
        seen_techniques: set[str] = set()
        for row in snapshot.mitre_rows:
            t_id = row.technique_id
            if t_id in seen_techniques:
                continue
            seen_techniques.add(t_id)
            t_name = row.name.strip() or t_id
            t_tactic = (
                row.tactic.strip()
                if row.tactic and row.tactic != "Adversary Tactic"
                else ""
            )
            t_reason = row.reason.strip() or (
                "ข้อสันนิษฐานเชื่อมโยงจากฐานข้อมูล MITRE ATT&CK"
                if lang == "th"
                else "Analytical correlation from MITRE knowledge base"
            )
            finding_title = f"{t_tactic}: {t_name}" if t_tactic else t_name
            status_display = i18n["status_candidate"]

            mitre_view_rows.append(
                MitreMappingViewRow(
                    finding=finding_title,
                    case_evidence_support=t_reason,
                    technique_id=t_id,
                    technique_name=t_name,
                    status_display=status_display,
                    tactic=t_tactic or ("General" if lang == "en" else "ทั่วไป"),
                    source="MITRE ATT&CK Knowledge Base",
                    relevance="candidate",
                )
            )
    elif snapshot is None:
        raw_mitre_items: list[str] = []
        for sec_id in (
            "technical_analysis_mitre",
            "mitre_attack_mapping",
            "mapping_rationale",
        ):
            if sec_id in sections_by_id:
                raw_mitre_items.extend(sections_by_id[sec_id].items)

        seen_techniques = set()
        for item in raw_mitre_items:
            if not item or item.startswith("No ") or item.startswith("ไม่มี"):
                continue
            m_match = re.match(
                r"^(T\d+(?:\.\d+)?)\s*(?:[—:\-]\s*|\s+)(?:([^(:]+?)\s*(?:\(([^)]+)\))?\s*[:—\-]\s*)?(.*)$",
                item,
            )
            if m_match:
                t_id = m_match.group(1)
                if t_id in seen_techniques:
                    continue
                seen_techniques.add(t_id)
                t_name = (m_match.group(2) or "").strip() or t_id
                t_tactic = (m_match.group(3) or "").strip()
                t_rest = (m_match.group(4) or "").strip()
                finding_title = f"{t_tactic}: {t_name}" if t_tactic else t_name
                mitre_view_rows.append(
                    MitreMappingViewRow(
                        finding=finding_title,
                        case_evidence_support=t_rest
                        or (
                            "Analytical correlation from MITRE knowledge base"
                            if lang == "en"
                            else "ข้อสันนิษฐานเชื่อมโยงจากฐานข้อมูล MITRE ATT&CK"
                        ),
                        technique_id=t_id,
                        technique_name=t_name,
                        status_display=i18n["status_candidate"],
                        tactic=t_tactic or ("General" if lang == "en" else "ทั่วไป"),
                        source="MITRE ATT&CK Knowledge Base",
                        relevance="candidate",
                    )
                )

    return mitre_view_rows
