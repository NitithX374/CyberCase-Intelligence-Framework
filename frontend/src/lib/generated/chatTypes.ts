import type { CaseNarrativeDocumentSource, DocumentSourceMetadata } from "./caseTypes";

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

export type ChatMessageCreate = {
    content: string;
    idempotency_key: string;
    action?: string | null;
    intent: "ask" | "followup_answer" | "clarification_answer";
    in_reply_to_message_id?: string | null;
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
    message_kind: "conversation" | "followup_question" | "followup_answer" | "clarification_answer";
    analysis_result_id: string | null;
    in_reply_to_message_id?: string | null;
    metadata_json: MessageMetadata;
    created_at: string;
};

export type ChatRetryRequest = {
    content: string;
    idempotency_key: string;
    action?: string | null;
    intent: "ask" | "followup_answer" | "clarification_answer";
    in_reply_to_message_id?: string | null;
    clarification_id?: string | null;
    response_language: "thai" | "english";
    document_sources?: CaseNarrativeDocumentSource[];
    request_ordinal: number;
    clarification_answer: boolean;
};

export type ChatThreadDetail = {
    id: string;
    case_id?: string | null;
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
    case_id?: string | null;
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
