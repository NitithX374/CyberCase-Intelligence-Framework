import type { EvidenceSourceRead, PersistedChatMessage } from "@/lib/api";
import type { SourceMessageRef } from "@/lib/case-overview-contracts";
import {
  asArray,
  asRecord,
  asStringArray,
} from "@/lib/case-overview-parsing";
import {
  parseCaseCitations,
  parseCaseEvidence,
  sourceRefs,
} from "@/lib/case-overview-source";

export interface AnalysisSourceReference {
  role: "supporting" | "conflicting";
  source: SourceMessageRef;
}

export function sourceReferencesForAnalysisMessage(
  analysisMessage: PersistedChatMessage,
  evidenceSources: EvidenceSourceRead[],
): AnalysisSourceReference[] {
  if (analysisMessage.role !== "assistant") return [];
  const trace = asRecord(analysisMessage.metadata_json.analysis_trace);
  if (trace?.version !== "case_analysis_trace_v1" || trace.validation_status !== "validated") {
    return [];
  }
  const sources = parseCaseEvidence(evidenceSources);
  const references = asArray(trace.claims).flatMap((value) => {
    const claim = asRecord(value);
    if (!claim) return [];
    const supportingIds = asStringArray(claim.supporting_source_ids);
    const contradictingIds = asStringArray(claim.contradicting_source_ids);
    return [
      ...sourceRefs(
        supportingIds,
        parseCaseCitations(claim.supporting_citations, supportingIds, sources),
        sources,
      ).map((source) => ({ role: "supporting" as const, source })),
      ...sourceRefs(
        contradictingIds,
        parseCaseCitations(claim.contradicting_citations, contradictingIds, sources),
        sources,
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
