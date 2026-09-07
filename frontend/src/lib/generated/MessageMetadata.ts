import type { ChatActionMetadata } from "./ChatActionMetadata";
import type { DocumentSourceMetadata } from "./DocumentSourceMetadata";
import type { FollowUpMetadata } from "./FollowUpMetadata";
import type { RagAttemptMetadata } from "./RagAttemptMetadata";

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
    chat_action?: ChatActionMetadata;
    chat_followup?: FollowUpMetadata;
    rag_attempt?: RagAttemptMetadata;
} & {
    [key: string]: unknown;
};
