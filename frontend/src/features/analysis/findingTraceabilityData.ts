import type { CaseAnalysisClaim } from "@/lib/api/types";

export interface FindingTraceabilityData {
  semanticSupport: NonNullable<CaseAnalysisClaim["semantic_grounding"]>["verdict"];
  semanticReason?: NonNullable<CaseAnalysisClaim["semantic_grounding"]>["reason"];
}

export function findingTraceabilityData(claim: CaseAnalysisClaim): FindingTraceabilityData {
  return {
    semanticSupport: claim.semantic_grounding?.verdict ?? "unassessed",
    ...(claim.semantic_grounding ? { semanticReason: claim.semantic_grounding.reason } : {}),
  };
}
