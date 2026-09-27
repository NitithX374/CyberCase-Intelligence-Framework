import type { CaseAnalysisResultRead, CaseMitreAssociation, CaseSourceRead } from "@/lib/api/types";
import type { SourceMessageRef } from "@/features/sources/types";
import type { CaseFinding } from "@/features/analysis/types";
import { asArray, asRecord, asString } from "@/lib/parse";
import { buildCaseOverview } from "@/features/analysis/overview";

export type TechnicalContextStatus =
  | "not_applicable"
  | "insufficient_context"
  | "retrieved_from_rag"
  | "retrieved_with_matches"
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
}

export interface RetrievedTechnicalContextCard {
  techniqueId: string;
  techniqueName: string;
  tactic: string;
  fullTechnicalDefinition: string;
}

export interface TechnicalContextData {
  status: TechnicalContextStatus;
  hasContext: boolean;
  techniques: TechnicalContextCard[];
  retrievedOnlyTechniques: RetrievedTechnicalContextCard[];
  failureCode: string | null;
  failureStage: TechnicalFailureStage | null;
}

type AugmentationStatus = Exclude<TechnicalContextStatus, "invalid_trace" | "unavailable">;

const augmentationStatuses: ReadonlySet<string> = new Set<AugmentationStatus>([
  "not_applicable",
  "insufficient_context",
  "retrieved_from_rag",
  "retrieved_with_matches",
  "failed",
]);

interface MitreRow {
  id: string;
  name: string;
  tactic: string;
  description: string;
  retrievalScore: number | null;
  retrievedBy: "vector" | "graph";
}

export function buildTechnicalContext(
  result: CaseAnalysisResultRead | null,
  rows: CaseSourceRead[] | null,
): TechnicalContextData {
  if (!result || !rows) return emptyTechnicalContext("unavailable", "case_analysis_unavailable");
  const overview = buildCaseOverview(result, rows);
  const trace = result.trace_json;
  if (!overview.hasAnalysis || !trace)
    return emptyTechnicalContext("invalid_trace", "invalid_trace");
  const augmentation = asRecord(result.external_context_json?.technical_augmentation);
  if (!augmentation) {
    return emptyTechnicalContext("unavailable", "technical_augmentation_unavailable", "metadata");
  }
  const status = asString(augmentation.status);
  if (!isAugmentationStatus(status)) {
    return emptyTechnicalContext("invalid_trace", "invalid_technical_augmentation", "metadata");
  }

  const retrieved = mitreRows(augmentation.mitre_table);
  const associations = trace.mitre_associations ?? [];
  const findings = new Map(overview.findings.map((finding) => [finding.id, finding]));
  const rowsById = new Map(retrieved.map((row) => [row.id, row]));
  const mappedIds = new Set(associations.map((association) => association.technique_id));
  const techniques = associations.flatMap((association) => {
    const row = rowsById.get(association.technique_id);
    return row ? [mappedCard(association, row, findings)] : [];
  });
  const retrievedOnlyTechniques = retrieved
    .filter((row) => !mappedIds.has(row.id))
    .map(retrievedOnlyCard);
  return contextData(
    status,
    techniques,
    retrievedOnlyTechniques,
    asString(augmentation.failure_code) || null,
  );
}

function isAugmentationStatus(status: string): status is AugmentationStatus {
  return augmentationStatuses.has(status);
}

function mappedCard(
  association: CaseMitreAssociation,
  row: MitreRow,
  findings: Map<string, CaseFinding>,
): TechnicalContextCard {
  return {
    associationId: association.association_id,
    techniqueId: row.id,
    techniqueName: row.name || row.id,
    tactic: row.tactic,
    shortPlainMeaning: association.plain_meaning || attackDescription(row.description),
    retrievalScore: row.retrievalScore,
    retrievedBy: row.retrievedBy,
    fullTechnicalDefinition: attackDescription(row.description),
    whyRelevantHere: association.reason,
    caseBasisSources: caseBasis(
      association.claim_ids.flatMap((claimId) => findings.get(claimId)?.supportingSources ?? []),
    ),
  };
}

function caseBasis(sources: SourceMessageRef[]): SourceMessageRef[] {
  const unique = [
    ...new Map(sources.map((source) => [`${source.id}|${source.exactQuote}`, source])).values(),
  ];
  const quoted = new Set(unique.filter((source) => source.exactQuote).map((source) => source.id));
  return unique.filter((source) => source.exactQuote || !quoted.has(source.id));
}

function retrievedOnlyCard(row: MitreRow): RetrievedTechnicalContextCard {
  return {
    techniqueId: row.id,
    techniqueName: row.name || row.id,
    tactic: row.tactic,
    fullTechnicalDefinition: attackDescription(row.description),
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

function attackDescription(description: string): string {
  return description.replace(/^[A-Za-z][A-Za-z ]{0,30}: [^.]{1,120}\.\s+/, "").trim();
}
