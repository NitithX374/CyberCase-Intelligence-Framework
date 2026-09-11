import type { ChatMessageRead } from "./chatTypes";

export type AdmitExtractionRequest = {
    extraction_id: string;
};

export type CaseAnalysisAccepted = {
    run: CaseRunRead;
};

export type CaseAnalysisCreate = {
    idempotency_key: string;
    response_language: "thai" | "english";
    expected_evidence_revision?: number | null;
};

export type CaseAnalysisResultRead = {
    id: string;
    case_id: string;
    run_id: string;
    snapshot_id: string;
    schema_version: string;
    status: "validated" | "legacy_unbound";
    answer: string;
    summary: string;
    trace_json: {
        [key: string]: unknown;
    } | null;
    execution_receipt_json: {
        [key: string]: unknown;
    } | null;
    retrieval_context_id: string | null;
    pipeline_config: {
        [key: string]: unknown;
    };
    provider_metadata_json: {
        [key: string]: unknown;
    };
    created_at: string;
    freshness: "missing" | "current" | "stale";
};

export type CaseChatMessageAccepted = {
    message: ChatMessageRead;
    run: CaseRunRead;
};

export type CaseClarificationAccepted = {
    clarification: CaseClarificationRead;
    run: CaseRunRead;
};

export type CaseClarificationAnswer = {
    answer: string;
    idempotency_key: string;
    response_language: "thai" | "english";
};

export type CaseClarificationRead = {
    id: string;
    case_id: string;
    origin_analysis_result_id: string;
    origin_snapshot_id: string;
    gap_key: string;
    gap_id: string;
    topic: string;
    question: string;
    metadata_json: {
        [key: string]: unknown;
    };
    state: "pending" | "answered" | "superseded";
    answer_evidence_source_id: string | null;
    question_message_id: string | null;
    answer_message_id: string | null;
    answer_fingerprint: string | null;
    answered_at: string | null;
    created_at: string;
    updated_at: string;
};

export type CaseRunRead = {
    id: string;
    case_id: string;
    operation: "analysis" | "ask";
    snapshot_id: string;
    request_message_id: string | null;
    context_analysis_result_id: string | null;
    clarification_id: string | null;
    status: "queued" | "running" | "completed" | "failed";
    attempt_count: number;
    error_code: string | null;
    error_message: string | null;
    created_at: string;
    started_at: string | null;
    finished_at: string | null;
    updated_at: string;
};
