import type { CaseAnalysisClaim } from "@/lib/api/types";

export interface FindingTraceabilityData {
  direct: number;
  recovered: number;
  legacy: number;
  unresolved: number;
  semanticSupport: NonNullable<CaseAnalysisClaim["semantic_grounding"]>["verdict"];
  semanticReason?: NonNullable<CaseAnalysisClaim["semantic_grounding"]>["reason"];
}

export function findingTraceabilityData(claim: CaseAnalysisClaim): FindingTraceabilityData {
  const counts: FindingTraceabilityData = {
    direct: 0,
    recovered: 0,
    legacy: 0,
    unresolved: 0,
    semanticSupport: claim.semantic_grounding?.verdict ?? "unassessed",
    ...(claim.semantic_grounding ? { semanticReason: claim.semantic_grounding.reason } : {}),
  };
  const resolved = new Set<string>();
  const unresolved = new Set<string>();
  for (const citation of claim.supporting_citations ?? []) {
    if (citation.pointer_state === "unresolved") {
      for (const id of citation.evidence_unit_ids ?? []) {
        unresolved.add(JSON.stringify([citation.source_id, "unit", id]));
      }
      if (!citation.evidence_unit_ids?.length) {
        unresolved.add(JSON.stringify([citation.source_id, "quote", citation.exact_quote]));
      }
      continue;
    }
    if (!citation.exact_quote) continue;
    const key = JSON.stringify([
      citation.source_id,
      citation.start,
      citation.end,
      citation.evidence_unit_ids,
      citation.exact_quote,
    ]);
    if (resolved.has(key)) continue;
    resolved.add(key);
    counts[citation.pointer_state ?? "legacy"]++;
  }
  for (const citation of claim.unverified_citations ?? []) {
    if (citation.role !== "supporting") continue;
    unresolved.add(
      JSON.stringify([
        citation.source_id,
        citation.evidence_unit_id ? "unit" : "quote",
        citation.evidence_unit_id ?? citation.written_quote,
      ]),
    );
  }
  for (const reference of claim.invalid_evidence ?? []) {
    if (reference.role !== "supporting" || reference.reason === "duplicate_id") continue;
    unresolved.add(JSON.stringify([reference.source_id, "unit", reference.evidence_unit_id]));
  }
  counts.unresolved = unresolved.size;
  return counts;
}
