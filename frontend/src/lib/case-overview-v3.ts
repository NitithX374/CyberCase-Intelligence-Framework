import type { PersistedChatMessage } from "@/lib/api";
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

export function isV3CaseOverviewMessage(message: PersistedChatMessage): boolean {
  if (message.role !== "assistant") return false;
  if (message.metadata_json.analysis_state_scope === "response_scoped") return false;
  if (message.metadata_json.canonical_case_state === false) return false;
  const trace = asRecord(message.metadata_json.analysis_trace);
  return (
    trace?.version === "analysis_trace_v3" &&
    trace.validation_status === "validated" &&
    trace.analysis_mode === "case_overview"
  );
}

export function buildV3CaseOverview(
  message: PersistedChatMessage,
  messages: PersistedChatMessage[],
  isProcessing: boolean,
): CaseOverviewData {
  const trace = asRecord(message.metadata_json.analysis_trace);
  if (!trace) throw new Error("Validated v3 overview message has no analysis trace");
  const associations = parseAssociations(trace.mitre_associations);
  const mitreTable = parseMitreTable(message.metadata_json.mitre_table);
  const findings = parseFindings(trace.claims, messages, associations, mitreTable);
  const gaps = parseGaps(trace.gaps);
  const claimTextById = new Map(findings.map((finding) => [finding.id, finding.text]));
  const mitreContext = buildMitreCards(associations, mitreTable, claimTextById);
  return {
    hasAnalysis: true,
    isProcessing,
    incidentSummary: asString(trace.summary),
    findings,
    gaps,
    mitreContext,
    technicalContextStatus: resolveTechnicalContextStatus(message, mitreContext.length),
    analysisMessageId: message.id,
    contractVersion: "v3",
  };
}

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
