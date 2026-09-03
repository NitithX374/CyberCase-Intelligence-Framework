import type { CaseNarrativeDocumentSource, PersistedChatMessage } from "./api";
import { isCaseEvidenceMessage } from "./case-evidence";
import type { DocumentIngestionState } from "./document-ingestion-store";

export interface IntakeMaterial {
  id: string;
  filename: string;
  status: string;
  pageCount: number | null;
  text: string | null;
  pending: boolean;
  messageId?: string;
}

export function intakeMaterials(
  messages: PersistedChatMessage[],
  ingestion: DocumentIngestionState,
  draft?: CaseNarrativeDocumentSource,
): IntakeMaterial[] {
  const materials = new Map<string, IntakeMaterial>();
  for (const message of messages.filter(isCaseEvidenceMessage)) {
    const sources: unknown[] = Array.isArray(message.metadata_json.document_sources)
      ? message.metadata_json.document_sources : [];
    for (const source of sources) {
      if (!source || typeof source !== "object") continue;
      if (!("document_id" in source) || typeof source.document_id !== "string" || !source.document_id.trim()) continue;
      if (!("filename" in source) || typeof source.filename !== "string" || !source.filename.trim()) continue;
      materials.set(source.document_id, {
        id: source.document_id,
        filename: source.filename,
        status: "In case record",
        pageCount: "page_count" in source && typeof source.page_count === "number"
          && Number.isInteger(source.page_count) && source.page_count > 0 ? source.page_count : null,
        text: message.content,
        pending: false,
        messageId: message.id,
      });
    }
  }
  if (draft && !materials.has(draft.document_id)) {
    materials.set(draft.document_id, {
      id: draft.document_id, filename: draft.filename, status: "Reviewed narrative draft",
      pageCount: draft.page_count || null, text: null, pending: false,
    });
  }
  const { file, fileName, result, error, isProcessing } = ingestion;
  const name = fileName ?? result?.filename;
  const id = result?.document_id ?? `pending:${name}`;
  if (name && !materials.has(id)) {
    materials.set(id, {
      id, filename: name, pageCount: result?.pages.length || null,
      text: result?.full_text ?? null, pending: true,
      status: isProcessing ? "Extracting text…" : error ? "Text extraction failed"
        : result ? "Text extraction complete" : file ? "Selected for extraction" : "Select file again to extract",
    });
  }
  return [...materials.values()];
}

export function intakeStatus({
  ingestion, hasEvidence, hasAnalysis, isSubmitting, hasNarrative, hasUnreviewedMaterial, failed,
}: {
  ingestion: DocumentIngestionState;
  hasEvidence: boolean;
  hasAnalysis: boolean;
  isSubmitting: boolean;
  hasNarrative: boolean;
  hasUnreviewedMaterial: boolean;
  failed: boolean;
}): { label: string; detail: string } {
  if (ingestion.isProcessing) return { label: "Extracting text…", detail: "The document is being prepared for review." };
  if (ingestion.error) return { label: "Extraction failed", detail: "Retry extraction or select another document." };
  if (isSubmitting) return { label: "Analyzing case…", detail: "The submitted narrative is being analyzed." };
  if (failed) return { label: "Analysis needs attention", detail: "Open Chat to review the failed analysis." };
  if (hasUnreviewedMaterial) return {
    label: ingestion.result ? "Review required" : "Extraction required",
    detail: ingestion.result ? "Review the extracted text before using it in the case."
      : "Extract text from the selected document to continue.",
  };
  if (hasAnalysis) return { label: "Analysis available", detail: "Continue to the case findings and open questions." };
  if (hasEvidence) return { label: "Narrative saved", detail: "Open Chat to continue the analysis of this case." };
  if (hasNarrative) return { label: "Ready for analysis", detail: "Your narrative will be saved when you start analysis." };
  return { label: "No case material added", detail: "Add a document or write a case narrative to begin." };
}
