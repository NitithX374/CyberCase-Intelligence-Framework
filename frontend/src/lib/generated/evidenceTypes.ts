export type CaseEvidenceCreate = {
    exact_text: string;
    provenance_json?: {
        [key: string]: unknown;
    };
    source_kind: "narrative" | "followup_answer";
    source_metadata_json?: {
        [key: string]: unknown;
    };
};

export type EvidenceSourceRead = {
    id: string;
    case_id: string;
    source_kind: string;
    document_id: string | null;
    origin_message_id: string | null;
    exact_text: string;
    provenance_json?: {
        [key: string]: unknown;
    };
    source_metadata_json?: {
        [key: string]: unknown;
    };
    created_at: string;
    archived_at: string | null;
};
