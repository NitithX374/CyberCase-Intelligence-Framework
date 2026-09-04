import axios from "axios";

import { getApiBaseUrl } from "./api-client";
import type { DocumentExtractionMethod } from "./api-types";

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
  words: OCRWord[];
  content_role: string;
  verification_status: string;
}

export interface DocumentGeneratedContent {
  text: string;
  content_role: string;
  verification_status: string;
}

export interface OCRWord {
  text: string;
  confidence: number | null;
  bbox: DocumentBoundingBox | null;
}

export interface DocumentRegionPreview {
  region_id: string;
  page_number: number;
  bbox: DocumentBoundingBox | null;
  region_type: string;
  recognition_method: string;
  recognizer: string;
  text: string;
  segmentation_confidence: number | null;
  recognition_confidence: number | null;
  words: OCRWord[];
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
  text_sha256?: string;
  routing_summary: DocumentRoutingSummary;
}

export interface IngestedDocumentPreview {
  document_id: string;
  filename: string;
  media_type: string;
  extraction_method: DocumentExtractionMethod;
  mode: DocumentIngestionMode;
  pages: DocumentPagePreview[];
  full_text: string;
  warnings: string[];
}

export interface PreviewDocumentIngestionOptions {
  signal?: AbortSignal;
  idempotencyKey?: string;
  caseKey?: string;
}

export function generateOcrIdempotencyKey(
  caseKey: string,
  file: File,
  mode: DocumentIngestionMode,
): string {
  const safeCaseKey = caseKey.trim() || "draft";
  return `${safeCaseKey}:${file.name}:${file.size}:${file.lastModified}:${mode}`;
}

export async function previewDocumentIngestion(
  file: File,
  mode: DocumentIngestionMode,
  optionsOrSignal?: AbortSignal | PreviewDocumentIngestionOptions,
): Promise<IngestedDocumentPreview> {
  const options: PreviewDocumentIngestionOptions =
    optionsOrSignal instanceof AbortSignal
      ? { signal: optionsOrSignal }
      : optionsOrSignal ?? {};

  const body = new FormData();
  body.append("file", file);

  const idempotencyKey =
    options.idempotencyKey ??
    (options.caseKey ? generateOcrIdempotencyKey(options.caseKey, file, mode) : undefined);

  const headers: Record<string, string> = {};
  if (idempotencyKey) {
    headers["X-Idempotency-Key"] = idempotencyKey;
  }
  if (options.caseKey) {
    headers["X-Case-Key"] = options.caseKey;
  }

  const response = await axios.post<IngestedDocumentPreview>(
    `${getApiBaseUrl()}/document-ingestion/preview`,
    body,
    {
      params: {
        mode,
        ...(options.caseKey ? { case_key: options.caseKey } : {}),
        ...(idempotencyKey ? { idempotency_key: idempotencyKey } : {}),
      },
      headers: Object.keys(headers).length > 0 ? headers : undefined,
      signal: options.signal,
      timeout: 120_000,
    },
  );
  return response.data;
}
