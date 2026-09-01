import type { PersistedChatMessage } from "@/lib/api";
import type { SourceMessageRef } from "@/lib/case-overview-contracts";
import {
  asArray,
  asRecord,
  asStringArray,
  mapSourceMessageIds,
  parseEvidenceCitations,
} from "@/lib/case-overview-parsing";

export interface AnalysisSourceReference {
  role: "supporting" | "conflicting";
  source: SourceMessageRef;
}

export function sourceReferencesForAnalysisMessage(
  analysisMessage: PersistedChatMessage,
  messages: PersistedChatMessage[],
): AnalysisSourceReference[] {
  if (analysisMessage.role !== "assistant") return [];
  const trace = asRecord(analysisMessage.metadata_json.analysis_trace);
  if (trace?.version !== "analysis_trace_v3" || trace.validation_status !== "validated") {
    return [];
  }
  const references = asArray(trace.claims).flatMap((value) => {
    const claim = asRecord(value);
    if (!claim) return [];
    return [
      ...mapSourceMessageIds(
        asStringArray(claim.supporting_source_message_ids),
        messages,
        parseEvidenceCitations(claim.supporting_citations),
      ).map((source) => ({ role: "supporting" as const, source })),
      ...mapSourceMessageIds(
        asStringArray(claim.contradicting_source_message_ids),
        messages,
        parseEvidenceCitations(claim.contradicting_citations),
      ).map((source) => ({ role: "conflicting" as const, source })),
    ];
  });
  const unique = new Map<string, AnalysisSourceReference>();
  for (const reference of references) {
    const key = [
      reference.role,
      reference.source.id,
      reference.source.exactQuote ?? "",
      reference.source.pageNumbers.join(","),
    ].join(":");
    if (!unique.has(key)) unique.set(key, reference);
  }
  return [...unique.values()].slice(0, 12);
}
