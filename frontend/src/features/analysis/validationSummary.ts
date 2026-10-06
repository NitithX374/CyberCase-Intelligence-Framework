import type { CaseAnalysisTrace } from "@/lib/api/types";
import { projectionReason, projectionStatus, type ProjectionCheckStatus } from "./projectionChecks";

export interface ProjectionReasonCount {
  reason: string;
  description: string;
  count: number;
}

export function validationSummary(trace: CaseAnalysisTrace) {
  const allViews = [
    ...(trace.involved_parties ?? []),
    ...(trace.timeline ?? []),
    ...(trace.impacts ?? []),
  ];
  const projections = allViews.filter((item) => !Object.keys(item.field_spans ?? {}).length);
  const counts: Record<ProjectionCheckStatus, number> = {
    supported: 0,
    not_supported: 0,
    unassessed: 0,
    not_recorded: 0,
  };
  const reasons = new Map<string, ProjectionReasonCount>();
  for (const item of projections) {
    const grounding = item.projection_grounding;
    counts[projectionStatus(grounding)]++;
    if (grounding?.verdict !== "unassessed") continue;
    const existing = reasons.get(grounding.reason);
    if (existing) existing.count++;
    else
      reasons.set(grounding.reason, {
        reason: grounding.reason,
        description: projectionReason(grounding),
        count: 1,
      });
  }
  const claims = { direct: 0, recovered: 0, legacy: 0, unresolved: 0 };
  for (const claim of trace.claims) {
    const citations = claim.supporting_citations ?? [];
    if (citations.some((citation) => citation.pointer_state === "direct")) claims.direct++;
    if (citations.some((citation) => citation.pointer_state === "recovered")) claims.recovered++;
    if (citations.some((citation) => !citation.pointer_state)) claims.legacy++;
    if (!citations.length) claims.unresolved++;
  }
  return {
    total: projections.length,
    counts,
    admitted: counts.supported,
    withheld: counts.not_supported + counts.unassessed,
    reasons: [...reasons.values()],
    claims,
    sourceUnits:
      trace.grounding && trace.grounding.evidence_ids_claimed > 0
        ? {
            claimed: trace.grounding.evidence_ids_claimed,
            resolved: trace.grounding.evidence_ids_resolved,
            invalid: trace.grounding.evidence_ids_invalid,
            rate: trace.grounding.evidence_id_resolution_rate ?? null,
          }
        : null,
  };
}
