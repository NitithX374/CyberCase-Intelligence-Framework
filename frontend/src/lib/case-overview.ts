import type { PersistedChatMessage, ThreadStatus } from "@/lib/api";
import type {
  CaseOverviewData,
  CaseFinding,
  ClaimType,
  EpistemicStatus,
} from "@/lib/case-overview-contracts";
import {
  buildLegacyCaseOverview,
  isLegacyCaseOverviewMessage,
} from "@/lib/case-overview-legacy";
import {
  buildV3CaseOverview,
  isV3CaseOverviewMessage,
} from "@/lib/case-overview-v3";
import { isCaseEvidenceMessage } from "./case-evidence";

export * from "@/lib/case-overview-contracts";

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
  return groupDefinitions.map((group) => ({
    ...group,
    findings: findings.filter((finding) => {
      const key = finding.epistemicStatus !== "reported" ? finding.epistemicStatus
        : finding.claimType === "unknown" ? "unknown_claim" : finding.claimType;
      return key === group.id;
    }),
  })).filter((group) => group.findings.length > 0);
}

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

export function buildCaseOverview(
  messages: PersistedChatMessage[],
  threadStatus?: ThreadStatus | null,
): CaseOverviewData {
  const isProcessing =
    threadStatus === "processing" || threadStatus === "awaiting_followup";
  const assistantMessages = messages.filter((message) => message.role === "assistant");
  const v3Message = [...assistantMessages].reverse().find(isV3CaseOverviewMessage);
  if (v3Message) return buildV3CaseOverview(v3Message, messages, isProcessing);

  const legacyMessage = [...assistantMessages]
    .reverse()
    .find(isLegacyCaseOverviewMessage);
  if (legacyMessage) {
    return buildLegacyCaseOverview(legacyMessage, messages, isProcessing);
  }

  return {
    hasAnalysis: false,
    isProcessing,
    incidentSummary: "",
    findings: [],
    gaps: [],
    mitreContext: [],
    technicalContextStatus: "hidden",
    analysisMessageId: null,
    contractVersion: null,
  };
}
