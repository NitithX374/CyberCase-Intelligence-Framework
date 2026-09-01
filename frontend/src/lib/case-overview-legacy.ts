import type { PersistedChatMessage } from "@/lib/api";
import type {
  CaseFinding,
  CaseGap,
  CaseOverviewData,
  ClaimType,
  EpistemicStatus,
  GapPriority,
  GapStatus,
} from "@/lib/case-overview-contracts";
import {
  asArray,
  asRecord,
  asString,
  asStringArray,
  buildMitreCards,
  mapSourceMessageIds,
  parseAssociations,
  parseMitreTable,
  techniquesForClaim,
} from "@/lib/case-overview-parsing";

export function isLegacyCaseOverviewMessage(message: PersistedChatMessage): boolean {
  if (message.role !== "assistant") return false;
  const trace = asRecord(message.metadata_json.analysis_trace);
  if (!trace) return message.metadata_json.analysis_kind === "grounded_main_analysis";
  return (
    trace.version === "analysis_trace_v2" &&
    trace.validation_status === "validated" &&
    trace.analysis_mode === "case_overview"
  );
}

export function buildLegacyCaseOverview(
  message: PersistedChatMessage,
  messages: PersistedChatMessage[],
  isProcessing: boolean,
): CaseOverviewData {
  const trace = asRecord(message.metadata_json.analysis_trace);
  const associations = parseAssociations(trace?.mitre_associations);
  const mitreTable = parseMitreTable(message.metadata_json.mitre_table);
  const findings = parseLegacyFindings(trace?.claims, messages, associations, mitreTable);
  const claimTextById = new Map(findings.map((finding) => [finding.id, finding.text]));
  const mitreContext = buildMitreCards(associations, mitreTable, claimTextById);
  return {
    hasAnalysis: true,
    isProcessing,
    incidentSummary: parseLegacySummary(message.content, findings),
    findings,
    gaps: parseLegacyGaps(message.metadata_json.chat_followup),
    mitreContext,
    technicalContextStatus: mitreContext.length > 0 ? "available" : "hidden",
    analysisMessageId: message.id,
    contractVersion: "legacy",
  };
}

function parseLegacyFindings(
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
    if (!id || !text) return [];
    const claimType = normalizeClaimType(asString(claim.claim_type));
    const epistemicStatus = normalizeEpistemicStatus(asString(claim.epistemic_status));
    return [{
      id,
      text,
      claimType,
      epistemicStatus,
      reasoningSummary: null,
      supportingSources: mapSourceMessageIds(asStringArray(claim.source_message_ids), messages),
      contradictingSources: [],
      mitreTechniques: techniquesForClaim(id, associations, mitreTable),
    }];
  });
}

function parseLegacyGaps(value: unknown): CaseGap[] {
  const followup = asRecord(value);
  const gapAnalysis = asRecord(followup?.gap_analysis);
  return asArray(gapAnalysis?.gaps).flatMap((item, index) => {
    const gap = asRecord(item);
    if (!gap) return [];
    const topic = asString(gap.topic);
    const description = asString(gap.description) || asString(gap.reason);
    if (!topic && !description) return [];
    return [{
      id: `legacy-gap-${index + 1}`,
      topic: topic || "Unresolved item",
      status: normalizeGapStatus(asString(gap.status)),
      description,
      affectedClaimIds: [],
      reason: asString(gap.reason) || description,
      priority: normalizePriority(asString(gap.priority)),
      askable: gap.askable === true,
    }];
  });
}

function parseLegacySummary(content: string, findings: CaseFinding[]): string {
  const heading = /^###\s*1\.\s*[^\n]*\n([\s\S]*?)(?=^###\s*\d+\.|$)/m.exec(content);
  const summary = heading?.[1]?.trim();
  if (summary) return summary;
  return findings.filter((finding) => finding.claimType === "reported")
    .slice(0, 3).map((finding) => finding.text).join(" ");
}

function normalizeClaimType(value: string): ClaimType {
  return value === "reported" || value === "analytical_inference" ? value : "unknown";
}

function normalizeEpistemicStatus(value: string): EpistemicStatus {
  const allowed: EpistemicStatus[] = [
    "reported", "suspected", "contradicted", "not_established", "unknown", "not_confirmed",
  ];
  return allowed.includes(value as EpistemicStatus) ? value as EpistemicStatus : "unknown";
}

function normalizeGapStatus(value: string): GapStatus {
  const allowed: GapStatus[] = ["NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"];
  return allowed.includes(value as GapStatus) ? value as GapStatus : "NOT_PROVIDED";
}

function normalizePriority(value: string): GapPriority {
  return value === "high" || value === "low" ? value : "medium";
}
