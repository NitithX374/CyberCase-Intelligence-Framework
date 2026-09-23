import type {
  CaseAnalysisClaim,
  CaseAnalysisGap,
  CaseAnalysisResultRead,
  CaseMitreAssociation,
  CaseSourceRead,
} from "@/lib/api";
import { parseCaseCitations, parseCaseSources, sourceRefs } from "@/features/sources/sourceRefs";
import type { CaseSourceRef } from "@/features/sources/types";
import type {
  CaseFinding,
  CaseGap,
  CaseOverviewData,
  CaseTraceAssociation,
  CaseTraceClaim,
  ClaimType,
  EpistemicStatus,
  ParsedCaseTrace,
} from "./types";

export const claimTypeLabels: Record<ClaimType, string> = {
  reported: "Reported information",
  analytical_inference: "Analytical inference",
  unknown: "Unknown information",
};

export const epistemicStatusLabels: Record<EpistemicStatus, string> = {
  reported: "Reported",
  suspected: "Suspected",
  contradicted: "Contradicted",
  not_established: "Not established",
  unknown: "Unknown",
  not_confirmed: "Not confirmed",
};

const groupDefinitions = [
  { id: "not_established", title: "Not established", collapsible: false },
  { id: "not_confirmed", title: "Not confirmed", collapsible: false },
  { id: "unknown", title: "Unknown", collapsible: false },
  { id: "contradicted", title: "Contradicted", collapsible: false },
  { id: "suspected", title: "Suspected", collapsible: false },
  { id: "reported", title: "Reported information", collapsible: true },
  { id: "analytical_inference", title: "Analytical inferences", collapsible: true },
  { id: "unknown_claim", title: "Unknown information", collapsible: false },
] as const;

export function groupCaseFindings(findings: CaseFinding[]) {
  return groupDefinitions
    .map((group) => ({
      ...group,
      findings: findings.filter((finding) => {
        const key =
          finding.epistemicStatus !== "reported"
            ? finding.epistemicStatus
            : finding.claimType === "unknown"
              ? "unknown_claim"
              : finding.claimType;
        return key === group.id;
      }),
    }))
    .filter((group) => group.findings.length > 0);
}

export function buildCaseOverview(
  result: CaseAnalysisResultRead | null,
  rows: CaseSourceRead[] | null,
): CaseOverviewData {
  if (!result) return emptyCaseOverview();
  if (!rows) return unavailableCaseOverview("The case sources are not available yet.");
  try {
    const sources = parseCaseSources(rows);
    const trace = parseCaseTrace(result, sources);
    return {
      hasAnalysis: true,
      incidentSummary: trace.summary,
      findings: trace.claims.map((claim) => toFinding(claim, trace.associations, sources)),
      gaps: trace.gaps,
    };
  } catch (error) {
    const reason =
      error instanceof Error ? error.message : "The saved Case analysis format is invalid.";
    return unavailableCaseOverview(reason);
  }
}

function emptyCaseOverview(): CaseOverviewData {
  return { hasAnalysis: false, incidentSummary: "", findings: [], gaps: [] };
}

function unavailableCaseOverview(reason: string): CaseOverviewData {
  return { ...emptyCaseOverview(), unavailableReason: reason };
}

function toFinding(
  claim: CaseTraceClaim,
  associations: CaseTraceAssociation[],
  sources: CaseSourceRef[],
): CaseFinding {
  return {
    id: claim.claimId,
    text: claim.text,
    claimType: claim.claimType,
    epistemicStatus: claim.epistemicStatus,
    reasoningSummary: claim.reasoningSummary,
    supportingSources: sourceRefs(claim.supportingIds, claim.supportingCitations, sources),
    contradictingSources: sourceRefs(claim.contradictingIds, claim.contradictingCitations, sources),
    mitreTechniques: associations
      .filter((association) => association.claimIds.includes(claim.claimId))
      .map((association) => ({
        techniqueId: association.techniqueId,
        techniqueName: association.techniqueId,
        reason: association.reason,
        description: "",
      })),
  };
}

export function parseCaseTrace(
  result: CaseAnalysisResultRead,
  sources: CaseSourceRef[],
): ParsedCaseTrace {
  const trace = result.trace_json;
  // The version and validation status are literals in the service contract, so
  // the types already rule these out. They are still checked, because rendering
  // an analysis that says it was not validated is the one mistake worth cost.
  if (
    !trace ||
    trace.version !== "case_analysis_trace_v1" ||
    trace.validation_status !== "validated" ||
    trace.analysis_mode !== "case_overview"
  ) {
    throw new Error("The saved Case analysis trace is unavailable or unsupported.");
  }
  // The service validates the trace against its own contract before storing it,
  // and the generated types carry that contract, so nothing is re-checked here.
  // Sources come from their own query, so a claim can still cite one this page
  // has not loaded — that is the only filter left.
  const knownSourceIds = new Set(sources.map((source) => source.id));
  return {
    summary: trace.summary || result.summary || "Case summary not provided.",
    claims: (trace.claims ?? []).map((claim) => toClaim(claim, sources, knownSourceIds)),
    gaps: (trace.gaps ?? []).map(toGap),
    associations: (trace.mitre_associations ?? []).map(toAssociation),
    retrievalContextId: trace.retrieval_context_id ?? null,
  };
}

function toClaim(
  claim: CaseAnalysisClaim,
  sources: CaseSourceRef[],
  knownSourceIds: Set<string>,
): CaseTraceClaim {
  const supportingIds = (claim.supporting_source_ids ?? []).filter((id) => knownSourceIds.has(id));
  const contradictingIds = (claim.contradicting_source_ids ?? []).filter((id) =>
    knownSourceIds.has(id),
  );
  return {
    claimId: claim.claim_id,
    claimType: claim.claim_type,
    text: claim.text,
    epistemicStatus: claim.epistemic_status,
    reasoningSummary: claim.reasoning_summary ?? null,
    supportingIds,
    contradictingIds,
    supportingCitations: parseCaseCitations(claim.supporting_citations, supportingIds, sources),
    contradictingCitations: parseCaseCitations(
      claim.contradicting_citations,
      contradictingIds,
      sources,
    ),
  };
}

function toGap(gap: CaseAnalysisGap): CaseGap {
  return {
    id: gap.gap_id,
    topic: gap.topic,
    status: gap.status,
    description: gap.description,
    affectedClaimIds: gap.affected_claim_ids ?? [],
    reason: gap.reason,
    priority: gap.priority,
    askable: gap.askable,
    clarificationQuestion: gap.clarification_question ?? null,
  };
}

function toAssociation(association: CaseMitreAssociation): CaseTraceAssociation {
  return {
    id: association.association_id,
    techniqueId: association.technique_id,
    claimIds: association.claim_ids,
    reason: association.reason,
    plainMeaning: association.plain_meaning ?? "",
  };
}
