import axios from "axios";

import { getApiBaseUrl } from "./api-client";

export type DocumentIngestionMode = "unified" | "routed";

export interface DocumentBoundingBox {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

export interface DocumentRecognitionCandidate {
  recognition_method: string;
  recognizer: string;
  text: string;
  confidence: number | null;
  content_role: string;
  verification_status: string;
}

export interface DocumentGeneratedContent {
  text: string;
  content_role: string;
  verification_status: string;
}

export interface DocumentRegionPreview {
  region_id: string;
  page_number: number;
  bbox: DocumentBoundingBox | null;
  region_type: string;
  recognition_method: string;
  recognizer: string;
  text: string;
  confidence: number | null;
  verification_status: string;
  content_role: string;
  contains_handwriting: boolean | null;
  candidates: DocumentRecognitionCandidate[];
  selected_candidate_index: number | null;
  generated_contents: DocumentGeneratedContent[];
  warning: string | null;
}

export interface DocumentRoutingSummary {
  native: number;
  unified: number;
  ocr: number;
  htr: number;
  mixed: number;
  unknown: number;
}

export interface DocumentPagePreview {
  page_number: number;
  regions: DocumentRegionPreview[];
  merged_text: string;
  routing_summary: DocumentRoutingSummary;
}

export interface IngestedDocumentPreview {
  document_id: string;
  filename: string;
  media_type: string;
  extraction_method: string;
  mode: DocumentIngestionMode;
  pages: DocumentPagePreview[];
  full_text: string;
  warnings: string[];
}

export async function previewDocumentIngestion(
  file: File,
  mode: DocumentIngestionMode,
  signal?: AbortSignal,
): Promise<IngestedDocumentPreview> {
  const body = new FormData();
  body.append("file", file);
  const response = await axios.post<IngestedDocumentPreview>(
    `${getApiBaseUrl()}/document-ingestion/preview`,
    body,
    { params: { mode }, signal, timeout: 120_000 },
  );
  return response.data;
}
