import type { PersistedChatMessage } from "@/lib/api";

export interface MitreLinkedClaimView {
  claimId: string;
  text: string;
  claimType: "reported" | "analytical_inference" | "unknown";
  epistemicStatus:
    | "reported"
    | "suspected"
    | "contradicted"
    | "not_established"
    | "unknown"
    | "not_confirmed";
}

export interface MitreCandidateView {
  associationId: string;
  techniqueId: string;
  techniqueName: string;
  claims: MitreLinkedClaimView[];
  reason: string;
}

const claimTypes = new Set([
  "reported",
  "analytical_inference",
  "unknown",
]);
const epistemicStatuses = new Set([
  "reported",
  "suspected",
  "contradicted",
  "not_established",
  "unknown",
  "not_confirmed",
]);

export function mitreCandidatesForMessage(
  message: PersistedChatMessage,
): MitreCandidateView[] | null {
  if (message.role !== "assistant") return null;
  const trace = asRecord(message.metadata_json.analysis_trace);
  if (!isValidatedTrace(trace)) return null;

  const claims = parseClaims(trace.claims);
  const associations = asArray(trace.mitre_associations);
  const mitreRows = asArray(message.metadata_json.mitre_table);
  if (!claims || !associations || !mitreRows) return null;

  const admittedRows = admittedMitreRows(mitreRows);
  const associationIds = new Set<string>();
  const candidates: MitreCandidateView[] = [];
  for (const rawAssociation of associations) {
    const association = asRecord(rawAssociation);
    if (!association || !hasOnlyAssociationKeys(association)) return null;
    const associationId = requiredString(association.association_id);
    const techniqueId = requiredString(association.technique_id);
    const reason = requiredString(association.reason);
    const claimIds = stringArray(association.claim_ids);
    if (
      !associationId?.match(/^MA-\d{2,}$/) ||
      !techniqueId?.match(/^T\d{4}(?:\.\d{3})?$/) ||
      !reason ||
      !claimIds?.length ||
      new Set(claimIds).size !== claimIds.length ||
      association.status !== "candidate_only" ||
      association.support_role !== "external_technical_context" ||
      associationIds.has(associationId)
    ) {
      return null;
    }
    const techniqueName = admittedRows.get(techniqueId);
    const linkedClaims = claimIds.map((claimId) => claims.get(claimId));
    if (!techniqueName || linkedClaims.some((claim) => !claim)) return null;
    associationIds.add(associationId);
    candidates.push({
      associationId,
      techniqueId,
      techniqueName,
      claims: linkedClaims as MitreLinkedClaimView[],
      reason,
    });
  }
  return candidates;
}

function parseClaims(value: unknown): Map<string, MitreLinkedClaimView> | null {
  const rawClaims = asArray(value);
  if (!rawClaims) return null;
  const claims = new Map<string, MitreLinkedClaimView>();
  for (const rawClaim of rawClaims) {
    const claim = asRecord(rawClaim);
    if (!claim) return null;
    const claimId = requiredString(claim.claim_id);
    const text = requiredString(claim.text);
    const claimType = requiredString(claim.claim_type);
    const epistemicStatus = requiredString(claim.epistemic_status);
    if (
      !claimId?.match(/^A-\d{2,}$/) ||
      !text ||
      !claimType ||
      !claimTypes.has(claimType) ||
      !epistemicStatus ||
      !epistemicStatuses.has(epistemicStatus) ||
      claims.has(claimId)
    ) {
      return null;
    }
    claims.set(claimId, {
      claimId,
      text,
      claimType: claimType as MitreLinkedClaimView["claimType"],
      epistemicStatus:
        epistemicStatus as MitreLinkedClaimView["epistemicStatus"],
    });
  }
  return claims;
}

function admittedMitreRows(rows: unknown[]): Map<string, string> {
  const admitted = new Map<string, string>();
  for (const rawRow of rows) {
    const row = asRecord(rawRow);
    const techniqueId = requiredString(row?.technique_id);
    const name = requiredString(row?.name);
    const entityType = requiredString(row?.entity_type)?.toLowerCase();
    if (
      techniqueId?.match(/^T\d{4}(?:\.\d{3})?$/) &&
      name &&
      (entityType === "technique" || entityType === "subtechnique")
    ) {
      admitted.set(techniqueId, name);
    }
  }
  return admitted;
}

function isValidatedTrace(
  trace: Record<string, unknown> | null,
): trace is Record<string, unknown> {
  const analysisMode = trace?.analysis_mode;
  return Boolean(
    trace &&
      trace.version === "analysis_trace_v1" &&
      (analysisMode === "case_overview" || analysisMode === "question_answer") &&
      requiredString(trace.case_state_version_id) &&
      requiredString(trace.retrieval_context_id) &&
      trace.validation_status === "validated" &&
      trace.reference_membership === "validated" &&
      trace.semantic_entailment === "not_deterministically_established",
  );
}

function hasOnlyAssociationKeys(value: Record<string, unknown>): boolean {
  const allowed = new Set([
    "association_id",
    "technique_id",
    "claim_ids",
    "reason",
    "status",
    "support_role",
  ]);
  return Object.keys(value).every((key) => allowed.has(key));
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function asArray(value: unknown): unknown[] | null {
  return Array.isArray(value) ? value : null;
}

function requiredString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function stringArray(value: unknown): string[] | null {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string")) {
    return null;
  }
  const normalized = value.map((item) => item.trim());
  return normalized.some((item) => !item) ? null : normalized;
}
