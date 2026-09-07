import type { CaseNarrativeDocumentSource, ChatThreadDetail } from "@/lib/api";
import type { PendingChatSubmission } from "./chat-workspace-types";

export function restoreInterruptedSubmission(detail: ChatThreadDetail): PendingChatSubmission | null {
  const retry = detail.retry_request;
  if (!retry) return null;
  const documentSources: CaseNarrativeDocumentSource[] = (retry.document_sources ?? []).map((source) => {
    if (source.minimum_confidence === undefined || !source.warnings || !source.page_spans) {
      throw new Error("The saved retry document metadata is incomplete.");
    }
    return { ...source, minimum_confidence: source.minimum_confidence, warnings: source.warnings, page_spans: source.page_spans };
  });
  return {
    threadId: detail.id,
    content: retry.content,
    key: retry.idempotency_key,
    action: retry.action ?? undefined,
    kind: retry.clarification_answer ? "followup" : "message",
    documentSources,
    requestOrdinal: retry.request_ordinal,
    lastKnownMessageOrdinal: retry.request_ordinal - 1,
  };
}
