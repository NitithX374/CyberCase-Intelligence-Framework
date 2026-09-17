import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api";
import {
  asArray,
  asRecord,
  asString,
  asStringArray,
  parseCaseCitations,
  parseCaseEvidence,
  sourceRefs,
} from "./caseOverviewSource";
import type {
  CaseEvidenceSource,
  CaseFinding,
  CaseGap,
  CaseOverviewData,
  CaseTraceAssociation,
  CaseTraceClaim,
  ClaimType,
  EpistemicStatus,
  GapPriority,
  GapStatus,
  MitreExplainedCard,
  TechnicalContextStatus,
  ParsedCaseTrace,
} from "./caseOverviewTypes";

export const claimTypeLabels: Record<ClaimType, string> = {
  reported: "Current information",
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
  return groupDefinitions.map((group) => ({
    ...group,
    findings: findings.filter((finding) => {
      const key = finding.epistemicStatus !== "reported"
        ? finding.epistemicStatus
        : finding.claimType === "unknown"
          ? "unknown_claim"
          : finding.claimType;
      return key === group.id;
    }),
  })).filter((group) => group.findings.length > 0);
}

export function buildCaseOverview(
  result: CaseAnalysisResultRead | null,
  evidenceSources: CaseSourceRead[] | null,
  runStatus: string | null,
): CaseOverviewData {
  const isProcessing = runStatus === "queued" || runStatus === "running";
  if (!result) return emptyCaseOverview(isProcessing);
  if (!evidenceSources) return unavailableCaseOverview(isProcessing, "The Case evidence is not available yet.");
  try {
    const sources = parseCaseEvidence(evidenceSources);
    const trace = parseCaseTrace(result, sources);
    const findings = trace.claims.map((claim) => toFinding(claim, trace.associations, sources));
    const ragCards = buildRagCards(result);
    return {
      hasAnalysis: true,
      isProcessing,
      incidentSummary: trace.summary,
      findings,
      gaps: trace.gaps,
      mitreContext: trace.associations.length ? buildMitreCards(trace.associations, findings) : ragCards,
      technicalContextStatus: technicalContextStatus(trace.associations, trace.retrievalContextId, result, ragCards.length),
    };
  } catch (error) {
    const reason = error instanceof Error ? error.message : "The saved Case analysis format is invalid.";
    return unavailableCaseOverview(isProcessing, reason);
  }
}

function emptyCaseOverview(isProcessing: boolean): CaseOverviewData {
  return {
    hasAnalysis: false,
    isProcessing,
    incidentSummary: "",
    findings: [],
    gaps: [],
    mitreContext: [],
    technicalContextStatus: "hidden",
  };
}

function unavailableCaseOverview(isProcessing: boolean, reason: string): CaseOverviewData {
  return { ...emptyCaseOverview(isProcessing), unavailableReason: reason };
}

function toFinding(
  claim: CaseTraceClaim,
  associations: CaseTraceAssociation[],
  sources: CaseEvidenceSource[],
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

function buildMitreCards(associations: CaseTraceAssociation[], findings: CaseFinding[]): MitreExplainedCard[] {
  const claimText = new Map(findings.map((finding) => [finding.id, finding.text]));
  return associations.map((association) => ({
    techniqueId: association.techniqueId,
    techniqueName: association.techniqueId,
    description: "",
    caseAssociationReason: association.reason,
    isExternalContext: true as const,
    linkedClaimTexts: association.claimIds.map((id) => claimText.get(id)).filter((text): text is string => Boolean(text)),
  }));
}

function buildRagCards(result: CaseAnalysisResultRead): MitreExplainedCard[] {
  const augmentation = asRecord(result.external_context_json?.technical_augmentation);
  if (asString(augmentation?.status) !== "retrieved_from_rag") return [];
  const seen = new Set<string>();
  return asArray(augmentation?.mitre_table).flatMap((value) => {
    const row = asRecord(value);
    const techniqueId = asString(row?.technique_id) || asString(row?.name);
    if (!techniqueId || seen.has(techniqueId)) return [];
    seen.add(techniqueId);
    return [{
      techniqueId,
      techniqueName: asString(row?.name) || techniqueId,
      description: asString(row?.description),
      caseAssociationReason: "Accepted directly from the RAG service as external technical context; not Case evidence.",
      isExternalContext: true as const,
      linkedClaimTexts: [],
    }];
  });
}

function technicalContextStatus(
  associations: CaseTraceAssociation[],
  retrievalContextId: string | null,
  result: CaseAnalysisResultRead,
  ragRowCount: number,
): TechnicalContextStatus {
  if (associations.length) return "available";
  const augmentation = asRecord(result.external_context_json?.technical_augmentation);
  const augmentationStatus = asString(augmentation?.status);
  if (augmentationStatus === "failed") return "unavailable";
  if (augmentationStatus === "retrieved_from_rag") return ragRowCount ? "retrieved_from_rag" : "no_matches";
  if (augmentationStatus === "insufficient_context" || augmentationStatus === "retrieved_without_supported_match") return "no_matches";
  if (augmentationStatus === "not_applicable") return "hidden";
  const ragAttempt = asRecord(result.external_context_json?.rag_attempt);
  if (asString(ragAttempt?.status) === "unavailable") return "unavailable";
  return retrievalContextId ? "no_matches" : "hidden";
}

const claimTypes = new Set<ClaimType>(["reported", "analytical_inference", "unknown"]);
const epistemicStatuses = new Set<EpistemicStatus>(["reported", "suspected", "contradicted", "not_established", "unknown", "not_confirmed"]);
const gapStatuses = new Set<GapStatus>(["NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"]);
const gapPriorities = new Set<GapPriority>(["high", "medium", "low"]);

export function parseCaseTrace(
  result: CaseAnalysisResultRead,
  sources: CaseEvidenceSource[],
): ParsedCaseTrace {
  const trace = asRecord(result.trace_json);
  if (!trace || trace.version !== "case_analysis_trace_v1" || trace.validation_status !== "validated" || trace.analysis_mode !== "case_overview") {
    throw new Error("The saved Case analysis trace is unavailable or unsupported.");
  }
  const claims: CaseTraceClaim[] = [];
  const claimIds = new Set<string>();
  for (const rawClaim of asArray(trace.claims)) {
    try {
      const claim = parseClaim(rawClaim, sources);
      if (!claimIds.has(claim.claimId)) {
        claimIds.add(claim.claimId);
        claims.push(claim);
      }
    } catch (err) {
      console.warn("Skipping invalid claim in analysis trace:", err);
    }
  }

  const gaps: CaseGap[] = [];
  for (const rawGap of asArray(trace.gaps)) {
    try {
      const gap = parseGap(rawGap);
      gaps.push({
        ...gap,
        affectedClaimIds: gap.affectedClaimIds.filter((id) => claimIds.has(id)),
      });
    } catch (err) {
      console.warn("Skipping invalid gap in analysis trace:", err);
    }
  }

  const associations: CaseTraceAssociation[] = [];
  for (const rawAssociation of asArray(trace.mitre_associations)) {
    try {
      const association = parseAssociation(rawAssociation);
      const filteredClaimIds = association.claimIds.filter((id) => claimIds.has(id));
      if (filteredClaimIds.length > 0) {
        associations.push({
          ...association,
          claimIds: filteredClaimIds,
        });
      }
    } catch (err) {
      console.warn("Skipping invalid MITRE association in analysis trace:", err);
    }
  }

  return {
    summary: asString(trace.summary) || asString(result.summary) || "Case summary not provided.",
    claims,
    gaps,
    associations,
    retrievalContextId: asString(trace.retrieval_context_id) || null,
  };
}

function parseClaim(value: unknown, sources: CaseEvidenceSource[]): CaseTraceClaim {
  const claim = asRecord(value);
  const claimId = asString(claim?.claim_id);
  const claimType = asString(claim?.claim_type) as ClaimType;
  const text = asString(claim?.text);
  const epistemicStatus = asString(claim?.epistemic_status) as EpistemicStatus;
  if (!/^A-\d{2,}$/.test(claimId) || !text || !claimTypes.has(claimType) || !epistemicStatuses.has(epistemicStatus)) {
    throw new Error("Analysis claim is invalid.");
  }
  const rawSupportingIds = asStringArray(claim?.supporting_source_ids);
  const rawContradictingIds = asStringArray(claim?.contradicting_source_ids);
  const knownSourceIds = new Set(sources.map((source) => source.id));
  const supportingIds = rawSupportingIds.filter((id) => knownSourceIds.has(id));
  const contradictingIds = rawContradictingIds.filter((id) => knownSourceIds.has(id) && !supportingIds.includes(id));
  return {
    claimId,
    claimType,
    text,
    epistemicStatus,
    reasoningSummary: asString(claim?.reasoning_summary) || null,
    supportingIds,
    contradictingIds,
    supportingCitations: parseCaseCitations(claim?.supporting_citations, supportingIds, sources),
    contradictingCitations: parseCaseCitations(claim?.contradicting_citations, contradictingIds, sources),
  };
}

function parseGap(value: unknown): CaseGap {
  const gap = asRecord(value);
  const gapId = asString(gap?.gap_id);
  const topic = asString(gap?.topic);
  const status = asString(gap?.status) as GapStatus;
  const description = asString(gap?.description);
  const reason = asString(gap?.reason);
  const priority = asString(gap?.priority) as GapPriority;
  const askable = gap?.askable;
  if (!/^G-\d{2,}$/.test(gapId) || !topic || !description || !reason || !gapStatuses.has(status) || !gapPriorities.has(priority) || typeof askable !== "boolean") throw new Error("Analysis gap is invalid.");
  return { id: gapId, topic, status, description, affectedClaimIds: asStringArray(gap?.affected_claim_ids), reason, priority, askable };
}

function parseAssociation(value: unknown): CaseTraceAssociation {
  const association = asRecord(value);
  const id = asString(association?.association_id);
  const techniqueId = asString(association?.technique_id);
  const claimIds = asStringArray(association?.claim_ids);
  const reason = asString(association?.reason);
  if (!/^MA-\d{2,}$/.test(id) || !/^T\d{4}(?:\.\d{3})?$/.test(techniqueId) || !claimIds.length || !reason || association?.status !== "candidate_only" || association?.support_role !== "external_technical_context") throw new Error("External technical association is invalid.");
  return { id, techniqueId, claimIds, reason };
}
