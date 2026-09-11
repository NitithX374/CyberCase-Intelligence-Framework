export type CaseEvidenceCreate = {
    exact_text: string;
    provenance_json?: {
        [key: string]: unknown;
    };
    source_kind: "narrative" | "clarification_answer" | "explicit_chat_addition";
    source_metadata_json?: {
        [key: string]: unknown;
    };
};

export type CaseEvidenceSnapshotRead = {
    id: string;
    case_id: string;
    evidence_revision: number;
    format_version: string;
    manifest_json: unknown[];
    input_text: string;
    text_sha256: string;
    manifest_sha256: string;
    created_at: string;
};

export type EvidenceRevisionRead = {
    id: string;
    source_id: string;
    revision: number;
    exact_text: string;
    text_sha256: string;
    provenance_json: {
        [key: string]: unknown;
    };
    extraction_id: string | null;
    admitted_at: string;
    archived_at: string | null;
};

export type EvidenceSourceRead = {
    id: string;
    case_id: string;
    source_kind: string;
    document_id: string | null;
    origin_message_id: string | null;
    source_metadata_json: {
        [key: string]: unknown;
    };
    created_at: string;
    archived_at: string | null;
    revisions?: EvidenceRevisionRead[];
};
