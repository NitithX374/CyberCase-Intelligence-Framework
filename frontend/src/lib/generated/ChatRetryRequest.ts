import type { CaseNarrativeDocumentSource } from "./CaseNarrativeDocumentSource";

export type ChatRetryRequest = {
    content: string;
    idempotency_key: string;
    action?: ("ask" | "add_case_info") | null;
    document_sources?: CaseNarrativeDocumentSource[];
    request_ordinal: number;
    clarification_answer: boolean;
};
