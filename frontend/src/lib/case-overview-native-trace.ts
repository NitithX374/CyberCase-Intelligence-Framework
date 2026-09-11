import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead } from "@/lib/api";
import { asArray, asRecord, asString, asStringArray } from "@/lib/case-overview-parsing";
import type { CaseGap, ClaimType, EpistemicStatus, GapPriority, GapStatus } from "@/lib/case-overview-contracts";
import { parseNativeCitations, type NativeCitation, type NativeSnapshotSource } from "./case-overview-native-source";

export interface NativeTraceClaim {
  claimId: string;
  claimType: ClaimType;
  text: string;
  epistemicStatus: EpistemicStatus;
  reasoningSummary: string | null;
  supportingIds: string[];
  contradictingIds: string[];
  supportingCitations: NativeCitation[];
  contradictingCitations: NativeCitation[];
}

export interface NativeTraceAssociation {
  id: string;
  techniqueId: string;
  claimIds: string[];
  reason: string;
}

export interface ParsedNativeTrace {
  summary: string;
  claims: NativeTraceClaim[];
  gaps: CaseGap[];
  associations: NativeTraceAssociation[];
  retrievalContextId: string | null;
}

const claimTypes = new Set<ClaimType>(["reported", "analytical_inference", "unknown"]);
const epistemicStatuses = new Set<EpistemicStatus>(["reported", "suspected", "contradicted", "not_established", "unknown", "not_confirmed"]);
const gapStatuses = new Set<GapStatus>(["NOT_PROVIDED", "EXPLICITLY_UNKNOWN", "AMBIGUOUS", "CONFLICTING"]);
const gapPriorities = new Set<GapPriority>(["high", "medium", "low"]);

export function parseNativeTrace(
  result: CaseAnalysisResultRead,
  snapshot: CaseEvidenceSnapshotRead,
  sources: NativeSnapshotSource[],
): ParsedNativeTrace {
  const trace = asRecord(result.trace_json);
  if (!trace || trace.version !== "case_analysis_trace_v1" || trace.validation_status !== "validated" || trace.analysis_mode !== "case_overview") throw new Error("The saved Case analysis trace is unavailable or unsupported.");
  if (trace.evidence_sha256 !== snapshot.text_sha256) throw new Error("Analysis is not bound to this evidence snapshot.");
  const claims = asArray(trace.claims).map((claim) => parseClaim(claim, sources));
  const gaps = asArray(trace.gaps).map(parseGap);
  const associations = asArray(trace.mitre_associations).map(parseAssociation);
  const claimIds = new Set(claims.map((claim) => claim.claimId));
  if (claimIds.size !== claims.length) throw new Error("Analysis claims have duplicate identifiers.");
  for (const gap of gaps) if (!gap.affectedClaimIds.every((id) => claimIds.has(id))) throw new Error("Analysis gap references an unknown claim.");
  for (const association of associations) if (!association.claimIds.every((id) => claimIds.has(id))) throw new Error("Analysis reference points to an unknown claim.");
  return {
    summary: asString(trace.summary) || invalidSummary(),
    claims,
    gaps,
    associations,
    retrievalContextId: asString(trace.retrieval_context_id) || null,
  };
}

function parseClaim(value: unknown, sources: NativeSnapshotSource[]): NativeTraceClaim {
  const claim = asRecord(value);
  const claimId = asString(claim?.claim_id);
  const claimType = asString(claim?.claim_type) as ClaimType;
  const text = asString(claim?.text);
  const epistemicStatus = asString(claim?.epistemic_status) as EpistemicStatus;
  if (!/^A-\d{2,}$/.test(claimId) || !text || !claimTypes.has(claimType) || !epistemicStatuses.has(epistemicStatus)) throw new Error("Analysis claim is invalid.");
  const supportingIds = asStringArray(claim?.supporting_source_ids);
  const contradictingIds = asStringArray(claim?.contradicting_source_ids);
  if (supportingIds.some((id) => !sources.some((source) => source.id === id)) || contradictingIds.some((id) => !sources.some((source) => source.id === id))) throw new Error("Analysis claim cites evidence outside the snapshot.");
  if (supportingIds.some((id) => contradictingIds.includes(id))) throw new Error("Analysis claim assigns one source to two roles.");
  return {
    claimId,
    claimType,
    text,
    epistemicStatus,
    reasoningSummary: asString(claim?.reasoning_summary) || null,
    supportingIds,
    contradictingIds,
    supportingCitations: parseNativeCitations(claim?.supporting_citations, supportingIds, sources),
    contradictingCitations: parseNativeCitations(claim?.contradicting_citations, contradictingIds, sources),
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

function parseAssociation(value: unknown): NativeTraceAssociation {
  const association = asRecord(value);
  const id = asString(association?.association_id);
  const techniqueId = asString(association?.technique_id);
  const claimIds = asStringArray(association?.claim_ids);
  const reason = asString(association?.reason);
  if (!/^MA-\d{2,}$/.test(id) || !/^T\d{4}(?:\.\d{3})?$/.test(techniqueId) || !claimIds.length || !reason || association?.status !== "candidate_only" || association?.support_role !== "external_technical_context") throw new Error("External technical association is invalid.");
  return { id, techniqueId, claimIds, reason };
}

function invalidSummary(): string {
  throw new Error("Analysis summary is empty.");
}

