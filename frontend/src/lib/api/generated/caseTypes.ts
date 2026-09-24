export type CaseDocumentRead = {
    id: string;
    case_id: string;
    filename: string;
    mime_type: string;
    size_bytes: number;
    created_at: string;
};

export type CaseRead = {
    id: string;
    user_id?: string | null;
    title: string;
    status: "idle" | "answered";
    source_revision: number;
    latest_analysis_result_id?: string | null;
    analysis_freshness: "missing" | "current" | "stale";
    created_at: string;
    updated_at: string;
};
