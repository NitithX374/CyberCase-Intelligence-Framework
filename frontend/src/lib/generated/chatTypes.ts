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
    gap_id?: string;
    gap_key?: string;
    topic?: string;
    selected_gap_detail?: {
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
