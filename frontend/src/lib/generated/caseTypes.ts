export type CaseDocumentRead = {
    id: string;
    case_id: string;
    filename: string;
    mime_type: string;
    size_bytes: number;
    content_sha256: string;
    archived_at: string | null;
    created_at: string;
    extractions?: DocumentExtractionRead[];
};

export type CaseNarrativeDocumentPageSpan = {
    page_number: number;
    start_offset: number;
    end_offset: number;
    text_sha256: string;
};

export type CaseNarrativeDocumentSource = {
    document_id: string;
    filename: string;
    extraction_method: "native_pdf" | "native_docx" | "document_recognition" | "hybrid";
    page_count: number;
    verification_status: "native" | "machine_read" | "needs_review";
    confidence_status: "reported" | "not_reported" | "not_applicable";
    minimum_confidence?: number | null;
    warnings?: string[];
    page_spans?: CaseNarrativeDocumentPageSpan[];
};

export type CaseRead = {
    id: string;
    user_id?: string | null;
    title: string;
    status: "idle" | "processing" | "awaiting_followup" | "answered" | "failed";
    chat_thread_id: string | null;
    evidence_revision: number;
    latest_analysis_result_id?: string | null;
    active_run_id?: string | null;
    latest_run_id?: string | null;
    processing_status: "idle" | "queued" | "running" | "failed";
    has_pending_clarification?: boolean;
    analysis_freshness: "missing" | "current" | "stale";
    created_at: string;
    updated_at: string;
};

export type DocumentExtractionRead = {
    id: string;
    document_id: string;
    revision: number;
    provider: string;
    config_json: {
        [key: string]: unknown;
    };
    extracted_text: string;
    text_sha256: string;
    provenance_json: {
        [key: string]: unknown;
    };
    warnings_json: unknown[];
    created_at: string;
};

export type DocumentSourceMetadata = {
    document_id?: string;
    filename?: string;
    page_count?: number;
    extraction_method?: string;
    verification_status?: string;
    confidence_status?: string;
    minimum_confidence?: number | null;
    warnings?: string[];
    page_spans?: CaseNarrativeDocumentPageSpan[];
} & {
    [key: string]: unknown;
};
