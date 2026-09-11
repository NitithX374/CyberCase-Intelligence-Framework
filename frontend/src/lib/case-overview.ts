import type { PersistedChatMessage, ThreadStatus } from "@/lib/api";
import type {
  CaseFinding,
  CaseGap,
  CaseOverviewData,
  ClaimType,
  EpistemicStatus,
  GapPriority,
  GapStatus,
  TechnicalContextStatus,
} from "@/lib/case-overview-contracts";
import {
  asArray,
  asRecord,
  asString,
  asStringArray,
  buildMitreCards,
  mapSourceMessageIds,
  parseEvidenceCitations,
  parseAssociations,
  parseMitreTable,
  techniquesForClaim,
} from "@/lib/case-overview-parsing";
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

const claimTypes = new Set<ClaimType>(["reported", "analytical_inference", "unknown"]);
const epistemicStatuses = new Set<EpistemicStatus>([
  "reported",
  "suspected",
  "contradicted",
  "not_established",
  "unknown",
  "not_confirmed",
]);
const gapStatuses = new Set<GapStatus>([
  "NOT_PROVIDED",
  "EXPLICITLY_UNKNOWN",
  "AMBIGUOUS",
  "CONFLICTING",
]);
const gapPriorities = new Set<GapPriority>(["high", "medium", "low"]);

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

function analysisRecord(message: PersistedChatMessage) {
  const value = message.metadata_json.analysis_trace;
  return value && typeof value === "object" && !Array.isArray(value)
    ? value as Record<string, unknown> : {};
}

function isCandidateAnalysisMessage(message: PersistedChatMessage): boolean {
  if (message.role !== "assistant") return false;
  const metadata = message.metadata_json;
  const trace = analysisRecord(message);
  const value = metadata.chat_action;
  const action = value && typeof value === "object"
    ? value as Record<string, unknown> : {};
  if (metadata.analysis_state_scope === "response_scoped" ||
      metadata.canonical_case_state === false ||
      trace.analysis_mode === "question_answer" ||
      action.analysis_mode === "question_answer" || action.action === "ask") return false;
  return metadata.analysis_state_scope === "canonical_case_overview" ||
    metadata.analysis_kind === "grounded_main_analysis" ||
    trace.analysis_mode === "case_overview" ||
    trace.version === "case_analysis_trace_v1" ||
    trace.version === "analysis_trace_v3" ||
    trace.version === "analysis_trace_v2";
}

export function isCanonicalCaseOverviewMessage(message: PersistedChatMessage): boolean {
  if (message.role !== "assistant") return false;
  if (message.metadata_json.analysis_state_scope === "response_scoped") return false;
  if (message.metadata_json.canonical_case_state === false) return false;
  const trace = asRecord(message.metadata_json.analysis_trace);
  return (
    (trace?.version === "case_analysis_trace_v1" || trace?.version === "analysis_trace_v3") &&
    trace.validation_status === "validated" &&
    trace.analysis_mode === "case_overview"
  );
}

export const isV3CaseOverviewMessage = isCanonicalCaseOverviewMessage;

export function buildTraceCaseOverview(
  message: PersistedChatMessage,
  messages: PersistedChatMessage[],
  isProcessing: boolean,
): CaseOverviewData {
  const trace = asRecord(message.metadata_json.analysis_trace);
  if (!trace) throw new Error("Validated overview message has no analysis trace");
  const associations = parseAssociations(trace.mitre_associations);
  const mitreTable = parseMitreTable(message.metadata_json.mitre_table);
  const findings = parseFindings(trace.claims, messages, associations, mitreTable);
  const gaps = parseGaps(trace.gaps);
  const claimTextById = new Map(findings.map((finding) => [finding.id, finding.text]));
  const mitreContext = buildMitreCards(associations, mitreTable, claimTextById);
  const version = trace.version === "analysis_trace_v3" ? "v3" : "case_analysis_trace_v1";
  return {
    hasAnalysis: true,
    isProcessing,
    incidentSummary: asString(trace.summary),
    findings,
    gaps,
    mitreContext,
    technicalContextStatus: resolveTechnicalContextStatus(message, mitreContext.length),
    analysisMessageId: message.id,
    contractVersion: version,
  };
}

export const buildV3CaseOverview = buildTraceCaseOverview;

function parseFindings(
  value: unknown,
  messages: PersistedChatMessage[],
  associations: ReturnType<typeof parseAssociations>,
  mitreTable: ReturnType<typeof parseMitreTable>,
): CaseFinding[] {
  return asArray(value).flatMap((item) => {
    const claim = asRecord(item);
    if (!claim) return [];
    const id = asString(claim.claim_id);
    const text = asString(claim.text);
    const claimType = asString(claim.claim_type) as ClaimType;
    const epistemicStatus = asString(claim.epistemic_status) as EpistemicStatus;
    if (!id || !text || !claimTypes.has(claimType) || !epistemicStatuses.has(epistemicStatus)) {
      return [];
    }
    return [{
      id,
      text,
      claimType,
      epistemicStatus,
      reasoningSummary: asString(claim.reasoning_summary) || null,
      supportingSources: mapSourceMessageIds(
        asStringArray(claim.supporting_source_message_ids),
        messages,
        parseEvidenceCitations(claim.supporting_citations),
      ),
      contradictingSources: mapSourceMessageIds(
        asStringArray(claim.contradicting_source_message_ids),
        messages,
        parseEvidenceCitations(claim.contradicting_citations),
      ),
      mitreTechniques: techniquesForClaim(id, associations, mitreTable),
    }];
  });
}

function parseGaps(value: unknown): CaseGap[] {
  return asArray(value).flatMap((item) => {
    const gap = asRecord(item);
    if (!gap) return [];
    const id = asString(gap.gap_id);
    const topic = asString(gap.topic);
    const description = asString(gap.description);
    const reason = asString(gap.reason);
    const status = asString(gap.status) as GapStatus;
    const priority = asString(gap.priority) as GapPriority;
    if (
      !id || !topic || !description || !reason ||
      !gapStatuses.has(status) || !gapPriorities.has(priority) ||
      typeof gap.askable !== "boolean"
    ) {
      return [];
    }
    return [{
      id,
      topic,
      status,
      description,
      affectedClaimIds: asStringArray(gap.affected_claim_ids),
      reason,
      priority,
      askable: gap.askable,
    }];
  });
}

function resolveTechnicalContextStatus(
  message: PersistedChatMessage,
  associationCount: number,
): TechnicalContextStatus {
  if (associationCount > 0) return "available";
  const applicability = asRecord(message.metadata_json.mitre_applicability);
  const ragAttempt = asRecord(message.metadata_json.rag_attempt);
  const decision = asString(applicability?.decision);
  const ragStatus = asString(ragAttempt?.status);
  if (decision === "SKIP" || ragStatus === "no_applicable_context") return "hidden";
  if (ragStatus === "unavailable") return "unavailable";
  if (decision === "RETRIEVE" || ragStatus === "used") return "no_matches";
  return "hidden";
}

export function buildCaseOverview(
  messages: PersistedChatMessage[],
  threadStatus?: ThreadStatus | null,
): CaseOverviewData {
  const isProcessing =
    threadStatus === "processing" || threadStatus === "awaiting_followup";
  const assistantMessages = messages.filter((message) => message.role === "assistant");
  const latestAnalysis = [...assistantMessages].sort((a, b) => b.ordinal - a.ordinal).find(isCandidateAnalysisMessage);

  if (!latestAnalysis) {
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

  if (isCanonicalCaseOverviewMessage(latestAnalysis)) {
    return buildTraceCaseOverview(latestAnalysis, messages, isProcessing);
  }

  const version = analysisRecord(latestAnalysis).version;
  const legacy = version === "analysis_trace_v2" ||
    (version == null && !latestAnalysis.metadata_json.analysis_trace_failure);
  const summary = legacy
    ? "This case analysis was generated with an earlier schema version. Please re-run analysis from Intake."
    : "The latest case analysis is unavailable or uses an unsupported format. Please re-run analysis from Intake.";
  return {
    hasAnalysis: true,
    isProcessing,
    incidentSummary: summary,
    findings: [],
    gaps: [],
    mitreContext: [],
    technicalContextStatus: "hidden",
    analysisMessageId: latestAnalysis.id,
    contractVersion: legacy ? "legacy" : version === "case_analysis_trace_v1" ? "case_analysis_trace_v1" : version === "analysis_trace_v3" ? "v3" : null,
  };
}
