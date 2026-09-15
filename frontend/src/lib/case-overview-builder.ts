import type { CaseAnalysisResultRead } from "@/lib/api";
import type { EvidenceSourceRead } from "@/lib/api";
import type { CaseFinding, CaseOverviewData, MitreExplainedCard, TechnicalContextStatus } from "@/lib/case-overview-contracts";
import { asRecord, asString } from "@/lib/case-overview-parsing";
import { parseCaseEvidence, sourceRefs, type CaseEvidenceSource } from "./case-overview-source";
import { parseCaseTrace, type CaseTraceAssociation, type CaseTraceClaim } from "./case-overview-trace";

export function buildCaseOverview(
  result: CaseAnalysisResultRead | null,
  evidenceSources: EvidenceSourceRead[] | null,
  runStatus: string | null,
): CaseOverviewData {
  const isProcessing = runStatus === "queued" || runStatus === "running";
  if (!result) return emptyCaseOverview(isProcessing);
  if (!evidenceSources) return unavailableCaseOverview(isProcessing, "The Case evidence is not available yet.");
  try {
    const sources = parseCaseEvidence(evidenceSources);
    const trace = parseCaseTrace(result, sources);
    const findings = trace.claims.map((claim) => toFinding(claim, trace.associations, sources));
    return {
      hasAnalysis: true,
      isProcessing,
      incidentSummary: trace.summary,
      findings,
      gaps: trace.gaps,
      mitreContext: buildMitreCards(trace.associations, findings),
      technicalContextStatus: technicalContextStatus(trace.associations, trace.retrievalContextId, result),
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
    mitreTechniques: associations.filter((association) => association.claimIds.includes(claim.claimId)).map((association) => ({
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
    isExternalContext: true,
    linkedClaimTexts: association.claimIds.map((id) => claimText.get(id)).filter((text): text is string => Boolean(text)),
  }));
}

function technicalContextStatus(
  associations: CaseTraceAssociation[],
  retrievalContextId: string | null,
  result: CaseAnalysisResultRead,
): TechnicalContextStatus {
  if (associations.length) return "available";
  const augmentation = asRecord(result.provider_metadata_json.technical_augmentation);
  const augmentationStatus = asString(augmentation?.status);
  if (augmentationStatus === "failed") return "unavailable";
  if (augmentationStatus === "insufficient_context" || augmentationStatus === "retrieved_without_supported_match") return "no_matches";
  if (augmentationStatus === "not_applicable") return "hidden";
  const ragAttempt = asRecord(result.provider_metadata_json.rag_attempt);
  if (asString(ragAttempt?.status) === "unavailable") return "unavailable";
  return retrievalContextId ? "no_matches" : "hidden";
}
