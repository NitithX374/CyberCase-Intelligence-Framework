import type { CaseNarrativeDocumentPageSpan } from "./CaseNarrativeDocumentPageSpan";

export type CaseNarrativeDocumentSource = {
    document_id: string;
    filename: string;
    extraction_method: "native_pdf" | "native_docx" | "document_recognition" | "hybrid";
    page_count: number;
    verification_status: "native" | "machine_read" | "needs_review";
    confidence_status: "reported" | "not_reported" | "not_applicable";
    minimum_confidence?: number | null;
    warnings?: string[];
    page_spans?: CaseNarrativeDocumentPageSpan[];
};
