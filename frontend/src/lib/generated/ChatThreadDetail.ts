import type { ChatMessageRead } from "./ChatMessageRead";
import type { ChatRetryRequest } from "./ChatRetryRequest";

export type ChatThreadDetail = {
    id: string;
    title: string;
    status: "idle" | "processing" | "awaiting_followup" | "answered" | "failed";
    created_at: string;
    updated_at: string;
    retry_request?: ChatRetryRequest | null;
    messages?: ChatMessageRead[];
};
