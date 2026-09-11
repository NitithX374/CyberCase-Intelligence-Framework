export type CaseReportCreate = {
    analysis_result_id?: string | null;
    idempotency_key?: string | null;
};

export type ReportClaim = {
    claim_id: string;
    section_id: "case_summary" | "indicators_found" | "mitre_attack_mapping" | "mapping_rationale" | "evidence_to_examine" | "preliminary_recommendations" | "system_limitations";
    text: string;
    support_type: "user_reported" | "analytical_inference" | "general_technical_knowledge" | "mitre_mapping_candidate" | "unknown";
    source_message_ids?: string[];
    source_evidence_ids?: string[];
    mitre_technique_ids?: string[];
};

export type ReportSection = {
    section_id: "case_summary" | "indicators_found" | "mitre_attack_mapping" | "mapping_rationale" | "evidence_to_examine" | "preliminary_recommendations" | "system_limitations";
    heading: string;
    paragraphs?: string[];
    items?: string[];
};

export type StructuredReport = {
    report_version: "preliminary_analysis_report_v1";
    status: "provisional_unverified";
    title: string;
    sections: ReportSection[];
    claims?: ReportClaim[];
    limitations?: string[];
};
