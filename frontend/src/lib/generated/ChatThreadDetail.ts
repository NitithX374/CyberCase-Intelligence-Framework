import type { ChatMessageRead } from "./ChatMessageRead";
import type { ChatRetryRequest } from "./ChatRetryRequest";

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
