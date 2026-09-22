export type CaseChatRead = {
    case_id: string;
    status: "idle" | "answered";
    messages?: ChatMessageRead[];
};

export type ChatMessageCreate = {
    content: string;
    client_request_id?: string | null;
    response_language: "thai" | "english";
};

export type ChatMessageRead = {
    id: string;
    case_id: string;
    ordinal: number;
    role: "user" | "assistant";
    content: string;
    message_kind: "conversation" | "followup_question" | "followup_answer";
    gap_key?: string | null;
    analysis_result_id: string | null;
    in_reply_to_message_id?: string | null;
    metadata_json: MessageMetadata;
    created_at: string;
};

export type MessageMetadata = {
    action?: "conversation";
    analysis_trace?: {
        [key: string]: unknown;
    };
};
