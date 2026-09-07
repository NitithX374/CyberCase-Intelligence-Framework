export type ChatThreadRead = {
    id: string;
    title: string;
    status: "idle" | "processing" | "awaiting_followup" | "answered" | "failed";
    created_at: string;
    updated_at: string;
};
