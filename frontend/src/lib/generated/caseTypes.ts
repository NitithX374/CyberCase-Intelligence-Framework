export type CaseDocumentRead = {
    id: string;
    case_id: string;
    filename: string;
    mime_type: string;
    size_bytes: number;
    archived_at: string | null;
    created_at: string;
    extractions?: DocumentExtractionRead[];
};

export type CaseRead = {
    id: string;
    user_id?: string | null;
    title: string;
    status: "idle" | "processing" | "awaiting_followup" | "answered" | "failed";
    evidence_revision: number;
    latest_analysis_result_id?: string | null;
    active_run_id?: string | null;
    latest_run_id?: string | null;
    processing_status: "idle" | "queued" | "running" | "failed";
    has_pending_followup: boolean;
    analysis_freshness: "missing" | "current" | "stale";
    created_at: string;
    updated_at: string;
};

export type DocumentExtractionRead = {
    id: string;
    document_id: string;
    provider: string;
    config_json: {
        [key: string]: unknown;
    };
    extracted_text: string;
    provenance_json: {
        [key: string]: unknown;
    };
    warnings_json: unknown[];
    created_at: string;
};
