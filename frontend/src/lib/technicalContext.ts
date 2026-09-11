import type { PersistedChatMessage } from "@/lib/api";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead } from "@/lib/api";
import { type SourceMessageRef } from "@/lib/case-overview";
import { getCaseEvidencePresentation } from "@/lib/case-evidence";
import { parseNativeSnapshot, sourceRefs, type NativeSnapshotSource } from "@/lib/case-overview-native-source";
import { parseNativeTrace, type NativeTraceAssociation, type NativeTraceClaim } from "@/lib/case-overview-native-trace";
import { asArray, asRecord, asString } from "@/lib/case-overview-parsing";

export type TechnicalContextStatus =
  | "not_applicable"
  | "insufficient_context"
  | "retrieved_with_matches"
  | "retrieved_without_supported_match"
  | "failed"
  | "invalid_trace"
  | "unavailable";

export type TechnicalFailureStage = "applicability" | "retrieval" | "mapping" | "metadata" | "augmentation";

export interface TechnicalContextCard {
  associationId: string;
  techniqueId: string;
  techniqueName: string;
  tactic: string;
  shortPlainMeaning: string;
  fullTechnicalDefinition: string;
  whyRelevantHere: string;
  caseBasisSources: SourceMessageRef[];
  isExternalReference: true;
}

export interface RetrievedTechnicalContextCard {
  techniqueId: string;
  techniqueName: string;
  tactic: string;
  fullTechnicalDefinition: string;
  isExternalReference: true;
}

export interface TechnicalContextData {
  status: TechnicalContextStatus;
  hasContext: boolean;
  techniques: TechnicalContextCard[];
  retrievedOnlyTechniques: RetrievedTechnicalContextCard[];
  totalCount: number;
  retrievedOnlyCount: number;
  failureCode: string | null;
  failureStage: TechnicalFailureStage | null;
}

type NativeAugmentationStatus = Exclude<TechnicalContextStatus, "invalid_trace" | "unavailable">;

interface NativeMitreRow {
  id: string;
  name: string;
  tactic: string;
  description: string;
}

interface NativeAugmentation {
  status: NativeAugmentationStatus;
  rows: NativeMitreRow[];
  retrievalContextId: string | null;
  associationIds: string[];
  failureCode: string | null;
}

export function buildNativeTechnicalContext(
  result: CaseAnalysisResultRead | null,
  snapshot: CaseEvidenceSnapshotRead | null,
): TechnicalContextData {
  if (!result || !snapshot) return emptyTechnicalContext("unavailable", "case_analysis_unavailable");
  let sources: NativeSnapshotSource[];
  let trace: ReturnType<typeof parseNativeTrace>;
  try {
    sources = parseNativeSnapshot(snapshot);
    trace = parseNativeTrace(result, snapshot, sources);
  } catch {
    return emptyTechnicalContext("invalid_trace", "invalid_trace");
  }

  const augmentationRecord = asRecord(result.provider_metadata_json.technical_augmentation);
  if (!augmentationRecord) {
    return emptyTechnicalContext("unavailable", "technical_augmentation_unavailable", "metadata");
  }

  try {
    const augmentation = parseNativeAugmentation(augmentationRecord, trace);
    const claims = new Map(trace.claims.map((claim) => [claim.claimId, claim]));
    const rowsById = new Map(augmentation.rows.map((row) => [row.id, row]));
    const mappedIds = new Set(trace.associations.map((association) => association.techniqueId));
    const techniques = trace.associations.map((association) => {
      const row = rowsById.get(association.techniqueId);
      if (!row) throw new Error("Native MITRE association is outside persisted retrieval context.");
      return nativeMappedCard(association, row, claims, sources);
    });
    const retrievedOnlyTechniques = augmentation.rows
      .filter((row) => !mappedIds.has(row.id))
      .map(retrievedOnlyCard);
    return contextData(
      augmentation.status,
      techniques,
      retrievedOnlyTechniques,
      augmentation.failureCode,
    );
  } catch {
    return emptyTechnicalContext("invalid_trace", "invalid_technical_augmentation", "metadata");
  }
}

function parseNativeAugmentation(
  value: Record<string, unknown>,
  trace: ReturnType<typeof parseNativeTrace>,
): NativeAugmentation {
  const rawStatus = asString(value.status);
  if (!isNativeAugmentationStatus(rawStatus)) throw new Error("Native augmentation status is invalid.");
  const rows = nativeMitreRows(value);
  const retrievalContextId = asString(value.retrieval_context_id) || null;
  const associationIds = asArray(value.association_ids).map(asString).filter(Boolean);
  const traceAssociationIds = trace.associations.map((association) => association.id);
  if (associationIds.length !== traceAssociationIds.length || associationIds.some((id, index) => id !== traceAssociationIds[index])) {
    throw new Error("Native augmentation associations are not bound to the analysis trace.");
  }
  if (retrievalContextId !== trace.retrievalContextId) throw new Error("Native retrieval context is not bound to the analysis trace.");
  if (rawStatus === "retrieved_with_matches" && (!retrievalContextId || !trace.associations.length)) throw new Error("Native augmentation match status is incomplete.");
  if (rawStatus === "retrieved_without_supported_match" && trace.associations.length) throw new Error("Native no-match status has associations.");
  if (rawStatus === "failed" && (!asString(value.failure_code) || trace.associations.length)) throw new Error("Native augmentation failure status is incomplete.");
  if (rawStatus === "not_applicable" && (rows.length || retrievalContextId || trace.associations.length)) throw new Error("Native not-applicable status has retrieved context.");
  if (rawStatus === "insufficient_context" && trace.associations.length) throw new Error("Native insufficient context has associations.");
  return {
    status: rawStatus,
    rows,
    retrievalContextId,
    associationIds,
    failureCode: asString(value.failure_code) || null,
  };
}

function isNativeAugmentationStatus(value: string): value is NativeAugmentationStatus {
  return value === "not_applicable" || value === "insufficient_context" || value === "retrieved_with_matches" || value === "retrieved_without_supported_match" || value === "failed";
}

function nativeMappedCard(
  association: NativeTraceAssociation,
  row: NativeMitreRow,
  claims: Map<string, NativeTraceClaim>,
  sources: NativeSnapshotSource[],
): TechnicalContextCard {
  const sourceIds = [...new Set(association.claimIds.flatMap((claimId) => claims.get(claimId)?.supportingIds ?? []))];
  if (!sourceIds.length) throw new Error("Native MITRE association has no Case evidence support.");
  const citations = association.claimIds.flatMap((claimId) => claims.get(claimId)?.supportingCitations ?? []);
  return {
    associationId: association.id,
    techniqueId: row.id,
    techniqueName: row.name || row.id,
    tactic: row.tactic,
    shortPlainMeaning: extractShortPlainMeaning(row.description),
    fullTechnicalDefinition: row.description,
    whyRelevantHere: association.reason,
    caseBasisSources: sourceRefs(sourceIds, citations, sources),
    isExternalReference: true,
  };
}

function retrievedOnlyCard(row: NativeMitreRow): RetrievedTechnicalContextCard {
  return {
    techniqueId: row.id,
    techniqueName: row.name || row.id,
    tactic: row.tactic,
    fullTechnicalDefinition: row.description,
    isExternalReference: true,
  };
}

export function buildTechnicalContext(messages: PersistedChatMessage[]): TechnicalContextData {
  const assistantMessages = messages.filter((message) => message.role === "assistant");
  const analysisMessage = [...assistantMessages].reverse().find((message) => {
    const trace = asRecord(message.metadata_json.analysis_trace);
    return message.metadata_json.analysis_kind === "grounded_main_analysis" || trace?.version === "analysis_trace_v2";
  });
  if (!analysisMessage) return emptyTechnicalContext("unavailable", "analysis_message_unavailable");

  const trace = asRecord(analysisMessage.metadata_json.analysis_trace);
  const rawClaims = asArray(trace?.claims);
  const rawAssociations = asArray(trace?.mitre_associations);
  const rows = legacyMitreRows(analysisMessage.metadata_json.mitre_table);
  const claims = new Map<string, string[]>();
  for (const rawClaim of rawClaims) {
    const claim = asRecord(rawClaim);
    const claimId = asString(claim?.claim_id);
    if (claimId) claims.set(claimId, asArray(claim?.source_message_ids).map(asString).filter(Boolean));
  }
  const associations = new Map<string, { id: string; reason: string; sourceIds: string[] }>();
  for (const rawAssociation of rawAssociations) {
    const association = asRecord(rawAssociation);
    const techniqueId = asString(association?.technique_id);
    if (!isTechniqueId(techniqueId)) continue;
    const sourceIds = asArray(association?.claim_ids).flatMap((claimId) => claims.get(asString(claimId)) ?? []);
    const current = associations.get(techniqueId);
    associations.set(techniqueId, {
      id: asString(association?.association_id) || techniqueId,
      reason: asString(association?.reason) || current?.reason || "",
      sourceIds: [...new Set([...(current?.sourceIds ?? []), ...sourceIds])],
    });
  }
  const rowsById = new Map(rows.map((row) => [row.id, row]));
  const techniques = [...associations.entries()].flatMap(([techniqueId, association]) => {
    const row = rowsById.get(techniqueId);
    if (!row || !association.reason) return [];
    return [legacyMappedCard(association.id, techniqueId, row, association.reason, association.sourceIds, messages)];
  });
  const mappedIds = new Set(techniques.map((item) => item.techniqueId));
  const retrievedOnlyTechniques = rows.filter((row) => !mappedIds.has(row.id)).map(retrievedOnlyCard);
  const failureCode = techniques.length < associations.size ? "legacy_mapping_incomplete" : null;
  const status: TechnicalContextStatus = techniques.length
    ? "retrieved_with_matches"
    : rows.length
      ? "retrieved_without_supported_match"
      : "insufficient_context";
  return contextData(status, techniques, retrievedOnlyTechniques, failureCode);
}

function legacyMappedCard(
  associationId: string,
  techniqueId: string,
  row: NativeMitreRow,
  reason: string,
  sourceIds: string[],
  messages: PersistedChatMessage[],
): TechnicalContextCard {
  return {
    associationId,
    techniqueId,
    techniqueName: row.name || row.id,
    tactic: row.tactic === "Adversary Tactic" ? "" : row.tactic,
    shortPlainMeaning: extractShortPlainMeaning(row.description),
    fullTechnicalDefinition: row.description,
    whyRelevantHere: reason,
    caseBasisSources: mapSourceMessageIds(sourceIds, messages),
    isExternalReference: true,
  };
}

function mapSourceMessageIds(sourceIds: string[], messages: PersistedChatMessage[]): SourceMessageRef[] {
  const messageMap = new Map(messages.map((message) => [message.id, message]));
  return sourceIds.flatMap((id) => {
    const message = messageMap.get(id);
    const presentation = message ? getCaseEvidencePresentation(message) : null;
    if (!message || !presentation) return [];
    return [{
      id: message.id,
      ordinal: message.ordinal,
      label: presentation.label,
      excerpt: message.content.length > 120 ? `${message.content.slice(0, 120)}…` : message.content,
      sourceType: presentation.sourceType,
      sourceTypeLabel: presentation.sourceTypeLabel,
      fullContent: message.content,
      displayContent: message.content.length > 640 ? `${message.content.slice(0, 640)}…` : message.content,
      exactQuote: null,
      documentId: null,
      filename: null,
      pageNumbers: [],
      evidencePages: [],
    }];
  });
}

function legacyMitreRows(value: unknown): NativeMitreRow[] {
  const rows: NativeMitreRow[] = [];
  const seen = new Set<string>();
  for (const rawRow of asArray(value)) {
    const row = asRecord(rawRow);
    const id = asString(row?.technique_id);
    if (!isTechniqueId(id) || seen.has(id)) continue;
    seen.add(id);
    rows.push({ id, name: asString(row?.name), tactic: asString(row?.tactic), description: asString(row?.description) });
  }
  return rows;
}

function nativeMitreRows(value: Record<string, unknown>): NativeMitreRow[] {
  return legacyMitreRows(value.mitre_table);
}

function contextData(
  status: TechnicalContextStatus,
  techniques: TechnicalContextCard[],
  retrievedOnlyTechniques: RetrievedTechnicalContextCard[],
  failureCode: string | null = null,
): TechnicalContextData {
  return {
    status,
    hasContext: techniques.length > 0 || retrievedOnlyTechniques.length > 0 || status !== "insufficient_context" && status !== "unavailable",
    techniques,
    retrievedOnlyTechniques,
    totalCount: techniques.length,
    retrievedOnlyCount: retrievedOnlyTechniques.length,
    failureCode,
    failureStage: failureStageForCode(failureCode),
  };
}

function emptyTechnicalContext(
  status: TechnicalContextStatus = "unavailable",
  failureCode: string | null = null,
  failureStage: TechnicalFailureStage | null = null,
): TechnicalContextData {
  return { status, hasContext: false, techniques: [], retrievedOnlyTechniques: [], totalCount: 0, retrievedOnlyCount: 0, failureCode, failureStage: failureStage ?? failureStageForCode(failureCode) };
}

function failureStageForCode(code: string | null): TechnicalFailureStage | null {
  if (!code) return null;
  if (code.startsWith("mitre_mapping")) return "mapping";
  if (code.startsWith("rag_") || code === "rag_timeout") return "retrieval";
  if (code.includes("applicability")) return "applicability";
  if (code.includes("augmentation") || code.includes("trace")) return "metadata";
  return "augmentation";
}

function extractShortPlainMeaning(description: string): string {
  const clean = description.trim();
  if (!clean) return "คำอธิบายพฤติกรรมตามกรอบมาตรฐาน MITRE ATT&CK";
  const firstSentence = clean.split(/(?<=[.!?])\s+|\n+/)[0] ?? clean;
  return firstSentence.length > 200 ? `${firstSentence.slice(0, 197)}...` : firstSentence;
}

function isTechniqueId(value: string): boolean {
  return /^T\d{4}(?:\.\d{3})?$/.test(value);
}

export { emptyTechnicalContext };
