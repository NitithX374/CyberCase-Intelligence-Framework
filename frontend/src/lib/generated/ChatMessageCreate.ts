import type { CaseNarrativeDocumentSource } from "./CaseNarrativeDocumentSource";

export type ChatMessageCreate = {
    content: string;
    idempotency_key: string;
    action?: ("ask" | "add_case_info") | null;
    document_sources?: CaseNarrativeDocumentSource[];
};
