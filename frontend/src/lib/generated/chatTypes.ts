import type { CaseFollowUpAnswer } from "./runTypes";

export type CaseChatRead = {
    case_id: string;
    status: "idle" | "processing" | "awaiting_followup" | "answered" | "failed";
    messages?: ChatMessageRead[];
};

export type ChatMessageCreate = {
    content: string;
    idempotency_key: string;
    intent: "ask" | "followup_answer";
    in_reply_to_message_id?: string | null;
    response_language: "thai" | "english";
    followup?: CaseFollowUpAnswer | null;
};

export type ChatMessageRead = {
    id: string;
    case_id: string;
    ordinal: number;
    role: "user" | "assistant";
    content: string;
    retrieval_context_id: string | null;
    message_kind: "conversation" | "followup_question" | "followup_answer";
    analysis_result_id: string | null;
    in_reply_to_message_id?: string | null;
    metadata_json: MessageMetadata;
    created_at: string;
};

export type FollowUpMetadata = {
    root_ordinal?: number;
    round?: number;
    source_analysis_id?: string;
    source_revision?: number;
    gap?: {
        [key: string]: unknown;
    };
    answer?: {
        [key: string]: unknown;
    };
};

export type MessageMetadata = {
    action?: "conversation" | "follow_up";
    analysis_trace?: {
        [key: string]: unknown;
    };
    chat_followup?: FollowUpMetadata;
};
