import type { CaseNarrativeDocumentPageSpan } from "./CaseNarrativeDocumentPageSpan";

export type DocumentSourceMetadata = {
    document_id?: string;
    filename?: string;
    page_count?: number;
    extraction_method?: string;
    verification_status?: string;
    confidence_status?: string;
    minimum_confidence?: number | null;
    warnings?: string[];
    page_spans?: CaseNarrativeDocumentPageSpan[];
} & {
    [key: string]: unknown;
};
