import type {
  CaseNarrativeDocumentSource,
  DocumentConfidenceStatus,
  DocumentVerificationStatus,
} from "./api-types";
import type {
  DocumentRegionPreview,
  IngestedDocumentPreview,
} from "./document-ingestion";

export interface CaseNarrativeDraft {
  text: string;
  source: CaseNarrativeDocumentSource;
  pages: CaseNarrativeDraftPage[];
}

interface CaseNarrativeDraftPage {
  pageNumber: number;
  text: string;
  textSha256: string;
}

function transcribedRegions(
  result: IngestedDocumentPreview,
): DocumentRegionPreview[] {
  return result.pages.flatMap((page) =>
    page.regions.filter(
      (region) =>
        region.content_role === "transcribed_text" && region.text.trim().length > 0,
    ),
  );
}

function uniqueWarnings(result: IngestedDocumentPreview): string[] {
  const warnings = [
    ...result.warnings,
    ...result.pages.flatMap((page) =>
      page.regions.flatMap((region) => (region.warning ? [region.warning] : [])),
    ),
  ];
  return [...new Set(warnings.map((warning) => warning.trim()).filter(Boolean))].slice(
    0,
    32,
  );
}

function verificationStatus(
  regions: DocumentRegionPreview[],
  warnings: string[],
): DocumentVerificationStatus {
  if (
    warnings.length > 0 ||
    regions.some(
      (region) =>
        region.verification_status === "needs_review" ||
        region.contains_handwriting === true,
    )
  ) {
    return "needs_review";
  }
  if (
    regions.length > 0 &&
    regions.every((region) => region.verification_status === "native")
  ) {
    return "native";
  }
  return "machine_read";
}

function confidence(
  regions: DocumentRegionPreview[],
): { status: DocumentConfidenceStatus; minimum: number | null } {
  if (
    regions.length > 0 &&
    regions.every((region) => region.verification_status === "native")
  ) {
    return { status: "not_applicable", minimum: null };
  }
  const machineRead = regions.filter(
    (region) => region.verification_status !== "native",
  );
  const reported = machineRead.map((region) => region.confidence);
  if (
    reported.length === 0 ||
    reported.some((value) => value === null || value === undefined)
  ) {
    return { status: "not_reported", minimum: null };
  }
  return {
    status: "reported",
    minimum: Math.min(...(reported as number[])),
  };
}

export function buildCaseNarrativeDraft(
  result: IngestedDocumentPreview,
): CaseNarrativeDraft {
  const text = result.full_text.trim();
  if (!text) {
    throw new Error("Document ingestion produced no merged text.");
  }
  const regions = transcribedRegions(result);
  const warnings = uniqueWarnings(result);
  const verification = verificationStatus(regions, warnings);
  const confidenceValue = confidence(regions);
  return {
    text,
    source: {
      document_id: result.document_id,
      filename: result.filename,
      extraction_method: result.extraction_method,
      page_count: result.pages.length,
      verification_status: verification,
      confidence_status: confidenceValue.status,
      minimum_confidence: confidenceValue.minimum,
      warnings,
      page_spans: [],
    },
    pages: result.pages.flatMap((page) => {
      const pageText = page.merged_text.trim();
      return pageText && page.text_sha256
        ? [{
            pageNumber: page.page_number,
            text: pageText,
            textSha256: page.text_sha256,
          }]
        : [];
    }),
  };
}

export function bindCaseNarrativeDocumentSource(
  draft: CaseNarrativeDraft,
  narrative: string,
): CaseNarrativeDocumentSource {
  let searchOffset = 0;
  const pageSpans = draft.pages.flatMap((page) => {
    const startOffset = narrative.indexOf(page.text, searchOffset);
    if (startOffset < 0) return [];
    const endOffset = startOffset + page.text.length;
    searchOffset = endOffset;
    return [{
      page_number: page.pageNumber,
      start_offset: startOffset,
      end_offset: endOffset,
      text_sha256: page.textSha256,
    }];
  });
  return { ...draft.source, page_spans: pageSpans };
}
