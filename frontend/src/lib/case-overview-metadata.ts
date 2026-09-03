import type { PersistedChatMessage } from "./api";
import { isCaseEvidenceMessage } from "./case-evidence";
import type { CaseOverviewData } from "./case-overview-contracts";

export function caseOverviewMetadata(messages: PersistedChatMessage[], overview: CaseOverviewData) {
  const evidence = messages.filter(isCaseEvidenceMessage);
  const documents = new Map<string, { id: string; filename: string }>();
  for (const message of evidence) {
    const sources: unknown[] = Array.isArray(message.metadata_json.document_sources)
      ? message.metadata_json.document_sources : [];
    for (const source of sources) {
      if (!source || typeof source !== "object") continue;
      if (!("document_id" in source) || typeof source.document_id !== "string" || !source.document_id.trim()) continue;
      if (!("filename" in source) || typeof source.filename !== "string" || !source.filename.trim()) continue;
      documents.set(source.document_id, { id: source.document_id, filename: source.filename });
    }
  }
  const analysis = messages.find((message) => message.id === overview.analysisMessageId);
  const createdAt = analysis && !Number.isNaN(Date.parse(analysis.created_at)) ? analysis.created_at : null;
  return {
    evidenceCount: evidence.length,
    documents: [...documents.values()],
    createdAt,
    hasNewMaterial: !!analysis && evidence.some((message) => message.ordinal > analysis.ordinal),
    citedSourceCount: new Set(overview.findings.flatMap((finding) => [
      ...finding.supportingSources, ...finding.contradictingSources,
    ]).map((source) => source.id)).size,
  };
}
