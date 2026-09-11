import type { CaseNarrativeDocumentSource, DocumentSourceMetadata } from "./caseTypes";
import type { StructuredReport } from "./reportTypes";

export type ChatActionMetadata = {
    action?: "initial_analysis" | "ask" | "add_case_info";
    route?: string;
    rag_invoked?: boolean;
    retrieval_context_reused?: boolean;
    analysis_mode?: "case_overview" | "question_answer";
    prompt_version?: string;
} & {
    [key: string]: unknown;
};

export type ChatCaseLinkRead = {
    thread_id: string;
    status: "linked" | "historical_unavailable";
    case_id?: string | null;
};

export type ChatMessageAccepted = {
    message: ChatMessageRead;
    run: ChatRunRead;
};

export type ChatMessageCreate = {
    content: string;
    idempotency_key: string;
    action?: ("ask" | "add_case_info") | null;
    intent?: "ask" | "clarification_answer";
    clarification_id?: string | null;
    response_language: "thai" | "english";
    document_sources?: CaseNarrativeDocumentSource[];
};

export type ChatMessageRead = {
    id: string;
    thread_id: string;
    ordinal: number;
    role: "user" | "assistant";
    content: string;
    retrieval_context_id: string | null;
    message_kind: "conversation" | "clarification_answer" | "followup_question";
    analysis_result_id: string | null;
    metadata_json: MessageMetadata;
    created_at: string;
};

export type ChatReportRead = {
    report_id: string;
    thread_id: string | null;
    version_number: number;
    idempotency_key: string;
    source_snapshot_hash: string;
    analysis_message_id?: string | null;
    case_id?: string | null;
    analysis_result_id?: string | null;
    evidence_snapshot_id?: string | null;
    source_reference_type: "legacy_chat" | "case_evidence";
    retrieval_context_id: string | null;
    prompt_version: string;
    provider: string;
    model: string;
    decoding_settings: {
        [key: string]: unknown;
    };
    persistence_status: "completed" | "failed";
    validation_status: "validated" | "failed";
    report: StructuredReport | null;
    validation_errors: string[];
    failure_code: string | null;
    failure_message: string | null;
    created_at: string;
    finished_at: string | null;
    latency_ms: number | null;
    input_tokens: number | null;
    output_tokens: number | null;
    source_snapshot?: {
        [key: string]: unknown;
    } | null;
};

export type ChatRetryRequest = {
    content: string;
    idempotency_key: string;
    action?: ("ask" | "add_case_info") | null;
    response_language: "thai" | "english";
    document_sources?: CaseNarrativeDocumentSource[];
    request_ordinal: number;
    clarification_answer: boolean;
};

export type ChatRunRead = {
    id: string;
    thread_id: string;
    request_message_id: string;
    status: "queued" | "running" | "completed" | "failed";
    error_code: string | null;
    error_message: string | null;
    created_at: string;
    updated_at: string;
};

export type ChatThreadDetail = {
    id: string;
    user_id?: string | null;
    title: string;
    status: "idle" | "processing" | "awaiting_followup" | "answered" | "failed";
    created_at: string;
    updated_at: string;
    retry_request?: ChatRetryRequest | null;
    messages?: ChatMessageRead[];
};

export type ChatThreadRead = {
    id: string;
    user_id?: string | null;
    title: string;
    status: "idle" | "processing" | "awaiting_followup" | "answered" | "failed";
    created_at: string;
    updated_at: string;
};

export type FollowUpMetadata = {
    kind?: "clarification" | "decision";
    action?: "ask_followup" | "proceed";
    question?: string;
    reason_code?: string;
    source_run_id?: string;
    root_ordinal?: number;
    round?: number;
    prior_exchange_count?: number;
    followup_context?: {
        [key: string]: string;
    } | null;
    gap_analysis?: {
        [key: string]: unknown;
    };
    rag_invoked?: boolean;
    selected_gap_detail?: {
        [key: string]: unknown;
    };
    rag_skipped?: boolean;
    failure_code?: string | null;
} & {
    [key: string]: unknown;
};

export type MessageMetadata = {
    evidence_kind?: "initial_case_narrative" | "clarification_answer" | "added_case_information" | "analyst_question";
    document_sources?: DocumentSourceMetadata[];
    clarification_context?: {
        [key: string]: string;
    };
    analysis_kind?: string;
    analysis_state_scope?: "canonical_case_overview" | "response_scoped";
    canonical_case_state?: boolean;
    evidence_sha256?: string;
    source_message_ids?: string[];
    analysis_trace?: {
        [key: string]: unknown;
    };
    analysis_trace_failure?: {
        [key: string]: unknown;
    };
    mitre_table?: {
        [key: string]: unknown;
    }[];
    mitre_applicability?: {
        [key: string]: unknown;
    };
    technical_augmentation?: {
        [key: string]: unknown;
    };
    chat_action?: ChatActionMetadata;
    chat_followup?: FollowUpMetadata;
    rag_attempt?: RagAttemptMetadata;
} & {
    [key: string]: unknown;
};

export type RagAttemptMetadata = {
    status?: "used" | "no_applicable_context" | "unavailable";
    failure_code?: string | null;
} & {
    [key: string]: unknown;
};
