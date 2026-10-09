import type { CaseSourceRead } from "@/lib/api/types";

interface ExtractionPageItem {
  page_number?: number;
  text?: string;
  merged_text?: string;
}

interface ExtractionPage {
  pageNumber: number;
  text: string;
}

export function documentPages(source: CaseSourceRead): ExtractionPage[] {
  const provenance = source.provenance_json as Record<string, unknown> | undefined;
  const rawPages = Array.isArray(provenance?.pages)
    ? (provenance.pages as ExtractionPageItem[])
    : [];

  if (rawPages.length === 0) {
    return [{ pageNumber: 1, text: source.exact_text }];
  }

  return rawPages.map((page, index) => ({
    pageNumber: typeof page.page_number === "number" ? page.page_number : index + 1,
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
