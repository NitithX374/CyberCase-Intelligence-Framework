import type { MessageMetadata } from "./MessageMetadata";

export type ChatMessageRead = {
    id: string;
    thread_id: string;
    ordinal: number;
    role: "user" | "assistant";
    content: string;
    retrieval_context_id: string | null;
    metadata_json: MessageMetadata;
    created_at: string;
};
