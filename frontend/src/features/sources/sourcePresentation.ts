import type { CaseSourceRead } from "@/lib/api/types";

interface ExtractionPageItem {
  page_number?: number;
  text?: string;
  merged_text?: string;
  verification_status?: string;
}

interface ExtractionPage {
  pageNumber: number;
  text: string;
  needsReview: boolean;
}

const OCR_STATUSES = ["machine_read", "needs_review"];

export function readByOcr(source: CaseSourceRead): boolean {
  const provenance = source.provenance_json as Record<string, unknown> | undefined;
  return (
    provenance?.extraction_method === "document_recognition" ||
    OCR_STATUSES.includes(String(provenance?.verification_status)) ||
    rawPages(source).some((page) => OCR_STATUSES.includes(String(page.verification_status)))
  );
}

function rawPages(source: CaseSourceRead): ExtractionPageItem[] {
  const provenance = source.provenance_json as Record<string, unknown> | undefined;
  return Array.isArray(provenance?.pages) ? (provenance.pages as ExtractionPageItem[]) : [];
}

export function documentPages(source: CaseSourceRead): ExtractionPage[] {
  const pages = rawPages(source);

  if (pages.length === 0) {
    return [{ pageNumber: 1, text: source.exact_text, needsReview: false }];
  }

  return pages.map((page, index) => ({
    pageNumber: typeof page.page_number === "number" ? page.page_number : index + 1,
    needsReview: page.verification_status === "needs_review",
    text:
      typeof page.text === "string"
        ? page.text
        : typeof page.merged_text === "string"
          ? page.merged_text
          : "",
  }));
}

export function fileKind(source: CaseSourceRead): string {
  const extension = source.filename?.split(".").pop()?.toUpperCase();
  const mimeType = source.mime_type ?? "";
  if (mimeType === "application/pdf") return "PDF";
  if (mimeType.startsWith("image/")) return extension ?? "Image";
  return extension ?? "File";
}
