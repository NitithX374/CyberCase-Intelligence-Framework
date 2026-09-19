import { describe, expect, it } from "vitest";
import type {
  CaseAnalysisResultRead,
  CaseAnalysisTrace,
  CaseMitreAssociation,
  CaseSourceRead,
} from "@/lib/api";
import { buildTechnicalContext } from "@/lib/technicalContext";

const sourceId = "11111111-1111-4111-8111-111111111111";
const caseId = "22222222-2222-4222-8222-222222222222";
const exactQuote = "The report records PowerShell network activity.";

function technicalContextFixture(
  status: string,
  rows: Record<string, string>[],
  associations: Omit<CaseMitreAssociation, "status" | "support_role">[] = [],
  failureCode?: string,
): { result: CaseAnalysisResultRead; sources: CaseSourceRead[] } {
  const sources: CaseSourceRead[] = [
    {
      id: sourceId,
      case_id: caseId,
      source_kind: "narrative",
      document_id: null,
      origin_message_id: null,
      exact_text: exactQuote,
      provenance_json: {},
      source_metadata_json: {},
      created_at: "2026-09-10T00:00:00Z",
      archived_at: null,
    },
  ];
  const retrievalContextId = status === "not_applicable" ? null : "retrieval-native-1";
  const traceAssociations: CaseMitreAssociation[] = associations.map((association) => ({
    association_id: association.association_id,
    technique_id: association.technique_id,
    claim_ids: association.claim_ids,
    reason: association.reason,
    plain_meaning: association.plain_meaning,
    status: "candidate_only" as const,
    support_role: "external_technical_context" as const,
  }));
  const result: CaseAnalysisResultRead = {
    id: "44444444-4444-4444-8444-444444444444",
    case_id: caseId,
    source_revision: 1,
    schema_version: "case_analysis_trace_v1",
    status: "validated",
    answer: exactQuote,
    summary: exactQuote,
    trace_json: {
      version: "case_analysis_trace_v1",
      validation_status: "validated",
      analysis_mode: "case_overview",
      summary: exactQuote,
      claims: [
        {
          claim_id: "A-01",
          claim_type: "reported",
          text: exactQuote,
          epistemic_status: "reported",
          reasoning_summary: null,
          supporting_source_ids: [sourceId],
          contradicting_source_ids: [],
          supporting_citations: [{ source_id: sourceId, exact_quote: exactQuote }],
          contradicting_citations: [],
        },
      ],
      gaps: [],
      mitre_associations: traceAssociations,
      retrieval_context_id: retrievalContextId,
    },
    retrieval_context_id: retrievalContextId,
    pipeline_config: {},
    external_context_json: {
      technical_augmentation: {
        version: "case_mitre_augmentation_v1",
        status,
        applicability: {
          decision: "RETRIEVE",
          source_message_ids: [sourceId],
          trigger_text: [exactQuote],
        },
        retrieval_context_id: retrievalContextId,
        mitre_table: rows,
        association_ids: associations.map((association) => association.association_id),
        ...(failureCode ? { failure_code: failureCode } : {}),
      },
    },
    created_at: "2026-09-10T00:00:00Z",
    freshness: "current",
  };
  return { result, sources };
}

describe("buildTechnicalContext", () => {
  const row = {
    technique_id: "T1059.001",
    name: "PowerShell",
    tactic: "Execution",
    description: "Command and scripting interpreter.",
  };

  it("shows mapping failure separately from retrieved-only context", () => {
    const fixture = technicalContextFixture("failed", [row], [], "mitre_mapping_invalid");
    const result = buildTechnicalContext(fixture.result, fixture.sources);
    expect(result.status).toBe("failed");
    expect(result.failureStage).toBe("mapping");
    expect(result.retrievedOnlyTechniques).toHaveLength(1);
  });

  it("distinguishes retrieval with no supported Case match", () => {
    const fixture = technicalContextFixture("retrieved_without_supported_match", [row]);
    const result = buildTechnicalContext(fixture.result, fixture.sources);
    expect(result.status).toBe("retrieved_without_supported_match");
    expect(result.retrievedOnlyCount).toBe(1);
  });

  it("accepts every RAG row without creating Case mappings", () => {
    const fixture = technicalContextFixture("retrieved_from_rag", [
      row,
      {
        technique_id: "S0096",
        name: "Systeminfo",
        tactic: "",
        description: "System information utility.",
      },
    ]);
    const result = buildTechnicalContext(fixture.result, fixture.sources);
    expect(result.status).toBe("retrieved_from_rag");
    expect(result.techniques).toHaveLength(0);
    expect(result.retrievedOnlyTechniques.map((item) => item.techniqueId)).toEqual([
      "T1059.001",
      "S0096",
    ]);
    expect(result.retrievedOnlyCount).toBe(2);
  });

  it("renders only the source-bound mapped subset", () => {
    const fixture = technicalContextFixture(
      "retrieved_with_matches",
      [
        row,
        {
          technique_id: "T1105",
          name: "Ingress Tool Transfer",
          tactic: "Command and Control",
          description: "Transfer tools into the environment.",
        },
      ],
      [
        {
          association_id: "MA-01",
          technique_id: "T1059.001",
          claim_ids: ["A-01"],
          reason: "The claim describes PowerShell activity.",
          plain_meaning: "Someone ran commands through PowerShell.",
        },
      ],
    );
    const result = buildTechnicalContext(fixture.result, fixture.sources);
    expect(result.status).toBe("retrieved_with_matches");
    expect(result.techniques.map((item) => item.techniqueId)).toEqual(["T1059.001"]);
    expect(result.retrievedOnlyTechniques.map((item) => item.techniqueId)).toEqual(["T1105"]);
    expect(result.techniques[0].caseBasisSources).toHaveLength(1);
  });

  it("withholds context when the persisted trace binding is invalid", () => {
    const fixture = technicalContextFixture("retrieved_without_supported_match", [row]);
    // A payload the current service cannot produce, kept to prove the guard holds
    // if an older deployment ever sends one.
    fixture.result.trace_json = {
      ...fixture.result.trace_json!,
      validation_status: "failed",
    } as unknown as CaseAnalysisTrace;
    const result = buildTechnicalContext(fixture.result, fixture.sources);
    expect(result.status).toBe("invalid_trace");
    expect(result.failureCode).toBe("invalid_trace");
  });
});

describe("a technique several claims rest on", () => {
  const row = {
    technique_id: "T1059.001",
    name: "PowerShell",
    tactic: "Execution",
    description: "Command and scripting interpreter.",
  };

  it("lists one case source per distinct quotation, not per claim", () => {
    const { result, sources } = technicalContextFixture(
      "retrieved_with_matches",
      [row],
      [
        {
          association_id: "MA-01",
          technique_id: "T1059.001",
          claim_ids: ["A-01", "A-02"],
          reason: "Both findings rest on the same sentence.",
          plain_meaning: "Someone ran commands.",
        },
      ],
    );
    // A second claim resting on the same sentence of the same source. React
    // saw two children under one source id before these were folded together.
    const trace = result.trace_json as Record<string, unknown>;
    const claims = trace.claims as Record<string, unknown>[];
    trace.claims = [claims[0], { ...claims[0], claim_id: "A-02" }];

    const context = buildTechnicalContext(result, sources);

    // The invariant a React key needs: no technique lists the same sentence of
    // the same source twice. It used to, once per claim that cited it.
    for (const technique of context.techniques) {
      const seen = technique.caseBasisSources.map((source) => `${source.id}|${source.exactQuote}`);
      expect(new Set(seen).size).toBe(seen.length);
    }
    expect(context.techniques[0].caseBasisSources[0].exactQuote).toBe(exactQuote);
  });
});
