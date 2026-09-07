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
