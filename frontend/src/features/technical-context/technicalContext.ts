import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api";
import { type SourceMessageRef, type CaseSourceRef } from "@/features/sources/types";
import { type CaseTraceAssociation, type CaseTraceClaim } from "@/features/analysis/types";
import { asArray, asRecord, asString } from "@/lib/parse";
import { parseCaseSources, sourceRefs } from "@/features/sources/sourceRefs";
import { parseCaseTrace } from "@/features/analysis/overview";

export type TechnicalContextStatus =
  | "not_applicable"
  | "insufficient_context"
  | "retrieved_from_rag"
  | "retrieved_with_matches"
  | "retrieved_without_supported_match"
  | "failed"
  | "invalid_trace"
  | "unavailable";

export type TechnicalFailureStage =
  "applicability" | "retrieval" | "mapping" | "metadata" | "augmentation";

export interface TechnicalContextCard {
  associationId: string;
  techniqueId: string;
  techniqueName: string;
  tactic: string;
  shortPlainMeaning: string;
  retrievalScore: number | null;
  retrievedBy: "vector" | "graph";
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

type AugmentationStatus = Exclude<TechnicalContextStatus, "invalid_trace" | "unavailable">;

interface MitreRow {
  id: string;
  name: string;
  tactic: string;
  description: string;
  /** How closely the case text matched this technique. Absent on rows the
   *  graph expansion reached, which were not scored against anything. */
  retrievalScore: number | null;
  retrievedBy: "vector" | "graph";
}

interface TechnicalAugmentation {
  status: AugmentationStatus;
  rows: MitreRow[];
  retrievalContextId: string | null;
  associationIds: string[];
  failureCode: string | null;
}

export function buildTechnicalContext(
  result: CaseAnalysisResultRead | null,
  rows: CaseSourceRead[] | null,
): TechnicalContextData {
  if (!result || !rows) return emptyTechnicalContext("unavailable", "case_analysis_unavailable");
  let sources: CaseSourceRef[];
  let trace: ReturnType<typeof parseCaseTrace>;
  try {
    sources = parseCaseSources(rows);
    trace = parseCaseTrace(result, sources);
  } catch {
    return emptyTechnicalContext("invalid_trace", "invalid_trace");
  }

  const augmentationRecord = asRecord(result.external_context_json?.technical_augmentation);
  if (!augmentationRecord) {
    return emptyTechnicalContext("unavailable", "technical_augmentation_unavailable", "metadata");
  }

  try {
    const augmentation = parseTechnicalAugmentation(augmentationRecord, trace);
    const claims = new Map(trace.claims.map((claim) => [claim.claimId, claim]));
    const rowsById = new Map(augmentation.rows.map((row) => [row.id, row]));
    const mappedIds = new Set(trace.associations.map((association) => association.techniqueId));
    const techniques = trace.associations.map((association) => {
      const row = rowsById.get(association.techniqueId);
      if (!row) throw new Error("MITRE association is outside persisted retrieval context.");
      return mappedCard(association, row, claims, sources);
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

function parseTechnicalAugmentation(
  value: Record<string, unknown>,
  trace: ReturnType<typeof parseCaseTrace>,
): TechnicalAugmentation {
  const rawStatus = asString(value.status);
  if (!isAugmentationStatus(rawStatus))
    throw new Error("Technical augmentation status is invalid.");
  const rows = augmentationRows(value);
  const retrievalContextId = asString(value.retrieval_context_id) || null;
  const associationIds = asArray(value.association_ids).map(asString).filter(Boolean);
  const traceAssociationIds = trace.associations.map((association) => association.id);
  if (
    associationIds.length !== traceAssociationIds.length ||
    associationIds.some((id, index) => id !== traceAssociationIds[index])
  ) {
    throw new Error("Technical augmentation associations are not bound to the analysis trace.");
  }
  if (retrievalContextId !== trace.retrievalContextId)
    throw new Error("Retrieval context is not bound to the analysis trace.");
  if (rawStatus === "retrieved_with_matches" && (!retrievalContextId || !trace.associations.length))
    throw new Error("Technical augmentation match status is incomplete.");
  if (
    rawStatus === "retrieved_from_rag" &&
    (!retrievalContextId || !rows.length || trace.associations.length)
  )
    throw new Error("Technical augmentation RAG status is incomplete.");
  if (rawStatus === "retrieved_without_supported_match" && trace.associations.length)
    throw new Error("Technical augmentation no-match status has associations.");
  if (rawStatus === "failed" && (!asString(value.failure_code) || trace.associations.length))
    throw new Error("Technical augmentation failure status is incomplete.");
  if (
    rawStatus === "not_applicable" &&
    (rows.length || retrievalContextId || trace.associations.length)
  )
    throw new Error("Non-applicable technical augmentation has retrieved context.");
  if (rawStatus === "insufficient_context" && trace.associations.length)
    throw new Error("Insufficient technical context has associations.");
  return {
    status: rawStatus,
    rows,
    retrievalContextId,
    associationIds,
    failureCode: asString(value.failure_code) || null,
  };
}

function isAugmentationStatus(value: string): value is AugmentationStatus {
  return (
    value === "not_applicable" ||
    value === "insufficient_context" ||
    value === "retrieved_from_rag" ||
    value === "retrieved_with_matches" ||
    value === "retrieved_without_supported_match" ||
    value === "failed"
  );
}

function mappedCard(
  association: CaseTraceAssociation,
  row: MitreRow,
  claims: Map<string, CaseTraceClaim>,
  sources: CaseSourceRef[],
): TechnicalContextCard {
  const sourceIds = [
    ...new Set(association.claimIds.flatMap((claimId) => claims.get(claimId)?.supportingIds ?? [])),
  ];
  if (!sourceIds.length) throw new Error("MITRE association has no case source support.");
  // Several claims can rest on the same sentence of the same source. That is
  // one piece of case basis for this technique, however many claims cite it.
  const citations = [
    ...new Map(
      association.claimIds
        .flatMap((claimId) => claims.get(claimId)?.supportingCitations ?? [])
        .map((citation) => [JSON.stringify([citation.sourceId, citation.exactQuote]), citation]),
    ).values(),
  ];
  return {
    associationId: association.id,
    techniqueId: row.id,
    techniqueName: row.name || row.id,
    tactic: row.tactic,
    // The analysis writes this for the reader; ATT&CK's own text is the fallback.
    shortPlainMeaning: association.plainMeaning || attackDescription(row.description),
    retrievalScore: row.retrievalScore,
    retrievedBy: row.retrievedBy,
    fullTechnicalDefinition: attackDescription(row.description),
    whyRelevantHere: association.reason,
    caseBasisSources: sourceRefs(sourceIds, citations, sources),
    isExternalReference: true,
  };
}

function retrievedOnlyCard(row: MitreRow): RetrievedTechnicalContextCard {
  return {
    techniqueId: row.id,
    techniqueName: row.name || row.id,
    tactic: row.tactic,
    fullTechnicalDefinition: attackDescription(row.description),
    isExternalReference: true,
  };
}

function mitreRows(value: unknown): MitreRow[] {
  const rows: MitreRow[] = [];
  const seen = new Set<string>();
  for (const rawRow of asArray(value)) {
    const row = asRecord(rawRow);
    const id = asString(row?.technique_id) || asString(row?.name);
    if (!id || seen.has(id)) continue;
    seen.add(id);
    rows.push({
      id,
      name: asString(row?.name),
      tactic: asString(row?.tactic),
      description: asString(row?.description),
      retrievalScore: typeof row?.score === "number" ? row.score : null,
      retrievedBy: row?.source === "graph" ? "graph" : "vector",
    });
  }
  return rows;
}

function augmentationRows(value: Record<string, unknown>): MitreRow[] {
  return mitreRows(value.mitre_table);
}

function contextData(
  status: TechnicalContextStatus,
  techniques: TechnicalContextCard[],
  retrievedOnlyTechniques: RetrievedTechnicalContextCard[],
  failureCode: string | null = null,
): TechnicalContextData {
  return {
    status,
    hasContext:
      techniques.length > 0 ||
      retrievedOnlyTechniques.length > 0 ||
      (status !== "insufficient_context" && status !== "unavailable"),
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
  return {
    status,
    hasContext: false,
    techniques: [],
    retrievedOnlyTechniques: [],
    totalCount: 0,
    retrievedOnlyCount: 0,
    failureCode,
    failureStage: failureStage ?? failureStageForCode(failureCode),
  };
}

function failureStageForCode(code: string | null): TechnicalFailureStage | null {
  if (!code) return null;
  if (code.startsWith("mitre_mapping")) return "mapping";
  if (code.startsWith("rag_") || code === "rag_timeout") return "retrieval";
  if (code.includes("applicability")) return "applicability";
  if (code.includes("augmentation") || code.includes("trace")) return "metadata";
  return "augmentation";
}

/** ATT&CK's own text, without the "Subtechnique: Web Shell. " that the ingester
 *  prepends so each embedding carries the entity's type and name. */
function attackDescription(description: string): string {
  return description.replace(/^[A-Za-z][A-Za-z ]{0,30}: [^.]{1,120}\.\s+/, "").trim();
}

export { emptyTechnicalContext };
