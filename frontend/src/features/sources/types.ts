export type SourceType = "case_description" | "followup_response";

export interface SourceMessageRef {
  id: string;
  ordinal: number;
  label: string;
  excerpt: string;
  sourceType: SourceType;
  sourceTypeLabel: string;
  fullContent: string;
  displayContent: string;
  exactQuote: string | null;
  documentId: string | null;
  filename: string | null;
  pageNumbers: number[];
  sourcePages: SourcePage[];
  isNativeSource?: boolean;
}

export interface SourcePage {
  pageNumber: number;
  text: string;
  exactQuote: string | null;
}

export interface CaseSourceRef {
  id: string;
  kind: string;
  ordinal: number;
  text: string;
  provenance: Record<string, unknown>;
  documentId: string | null;
  filename: string | null;
}

export interface CaseCitation {
  sourceId: string;
  exactQuote: string;
  documentId: string | null;
  filename: string | null;
  pageNumbers: number[];
}
