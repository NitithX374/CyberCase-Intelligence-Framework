import { describe, expect, it } from "vitest";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api/types";
import { analysisResult, association, claim, narrativeSource, trace } from "@/test/fixtures";
import {
  buildTechnicalContext,
  mitreAttackUrl,
} from "@/features/analysis/technical-context/technicalContext";

const exactQuote = "The report records PowerShell network activity.";

interface AssociationInput {
  association_id: string;
  technique_id: string;
  claim_ids: string[];
  reason: string;
  plain_meaning: string;
}

function technicalContextFixture(
  status: string,
  rows: Record<string, string>[],
  associations: AssociationInput[] = [],
  failureCode?: string,
): { result: CaseAnalysisResultRead; sources: CaseSourceRead[] } {
  const retrievalContextId = status === "not_applicable" ? null : "retrieval-native-1";
  const result = analysisResult({
    summary: exactQuote,
    trace_json: trace({
      summary: exactQuote,
      claims: [claim(exactQuote)],
      mitre_associations: associations.map(({ technique_id, ...rest }) =>
        association(technique_id, rest),
      ),
      retrieval_context_id: retrievalContextId,
    }),
    retrieval_context_id: retrievalContextId,
    external_context_json: {
      technical_augmentation: {
        status,
        retrieval_context_id: retrievalContextId,
        mitre_table: rows,
        association_ids: associations.map((item) => item.association_id),
        ...(failureCode ? { failure_code: failureCode } : {}),
      },
    },
  });
  return { result, sources: [narrativeSource(exactQuote)] };
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
    expect(result.techniques[0].whyRelevantHere).toBe("The claim describes PowerShell activity.");
    expect(result.techniques[0].casePassage).toBe("");
  });

  it("reads the reason of an association with no claims as the passage the retrieval service tied to it", () => {
    const passage = "“The attacker ran a PowerShell script on the clerk's computer.”";
    const fixture = technicalContextFixture(
      "retrieved_with_matches",
      [row],
      [
        {
          association_id: "MA-01",
          technique_id: "T1059.001",
          claim_ids: [],
          reason: passage,
          plain_meaning: "Someone ran commands through PowerShell.",
        },
      ],
    );
    const [card] = buildTechnicalContext(fixture.result, fixture.sources).techniques;
    expect(card.casePassage).toBe(passage);
    expect(card.whyRelevantHere).toBe("");
    expect(card.caseBasisSources).toEqual([]);
  });

  it("reads a retrieval that came back empty as no supported context", () => {
    const fixture = technicalContextFixture("insufficient_context", []);
    fixture.result.trace_json!.retrieval_context_id = null;
    const result = buildTechnicalContext(fixture.result, fixture.sources);
    expect(result.status).toBe("insufficient_context");
  });

  it("reads the stored augmentation as written, without re-checking it against the trace", () => {
    const fixture = technicalContextFixture(
      "retrieved_with_matches",
      [row],
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
    fixture.result.external_context_json = {
      technical_augmentation: {
        status: "retrieved_with_matches",
        retrieval_context_id: "another-retrieval",
        mitre_table: [row],
        association_ids: [],
      },
    };

    const result = buildTechnicalContext(fixture.result, fixture.sources);

    expect(result.status).toBe("retrieved_with_matches");
    expect(result.techniques.map((item) => item.techniqueId)).toEqual(["T1059.001"]);
  });

  it("reads an empty retrieval as no supported context, whatever the trace binds", () => {
    const fixture = technicalContextFixture("insufficient_context", []);
    const result = buildTechnicalContext(fixture.result, fixture.sources);
    expect(result.status).toBe("insufficient_context");
    expect(result.hasContext).toBe(false);
  });

  it("withholds context when the saved trace is not a case overview", () => {
    const fixture = technicalContextFixture("retrieved_from_rag", [row]);
    fixture.result.trace_json = {
      ...fixture.result.trace_json!,
      analysis_mode: "question_answer",
    };
    const result = buildTechnicalContext(fixture.result, fixture.sources);
    expect(result.status).toBe("invalid_trace");
    expect(result.failureCode).toBe("invalid_trace");
  });

  it("withholds a stored augmentation whose status the page does not know", () => {
    const fixture = technicalContextFixture("retrieved_without_supported_match", [row]);
    const result = buildTechnicalContext(fixture.result, fixture.sources);
    expect(result.status).toBe("invalid_trace");
    expect(result.failureCode).toBe("invalid_technical_augmentation");
    expect(result.failureStage).toBe("metadata");
    expect(result.hasContext).toBe(false);
    expect(result.retrievedOnlyTechniques).toHaveLength(0);
  });
});

describe("an association the page cannot tie to a case source", () => {
  const powershell = {
    technique_id: "T1059.001",
    name: "PowerShell",
    tactic: "Execution",
    description: "Command and scripting interpreter.",
  };
  const transfer = {
    technique_id: "T1105",
    name: "Ingress Tool Transfer",
    tactic: "Command and Control",
    description: "Transfer tools into the environment.",
  };
  const associations = [
    {
      association_id: "MA-01",
      technique_id: "T1059.001",
      claim_ids: ["A-01"],
      reason: "The claim describes PowerShell activity.",
      plain_meaning: "Someone ran commands through PowerShell.",
    },
    {
      association_id: "MA-02",
      technique_id: "T1105",
      claim_ids: ["A-02"],
      reason: "A tool was downloaded.",
      plain_meaning: "Someone brought a tool in.",
    },
  ];

  it("keeps every other technique, and shows this one without a case basis", () => {
    const { result, sources } = technicalContextFixture(
      "retrieved_with_matches",
      [powershell, transfer],
      associations,
    );
    const claims = result.trace_json!.claims;
    claims.push({
      ...claims[0],
      claim_id: "A-02",
      supporting_source_ids: ["QA-01"],
      supporting_citations: [
        { source_id: "QA-01", exact_quote: "I downloaded a tool.", pointer_state: "recovered" },
      ],
    });

    const context = buildTechnicalContext(result, sources);

    expect(context.status).toBe("retrieved_with_matches");
    expect(context.techniques.map((item) => item.techniqueId)).toEqual(["T1059.001", "T1105"]);
    expect(context.techniques[0].caseBasisSources).toHaveLength(1);
    expect(context.techniques[1].caseBasisSources).toEqual([]);
  });

  it("leaves out an association whose technique was not retrieved, and keeps the rest", () => {
    const { result, sources } = technicalContextFixture(
      "retrieved_with_matches",
      [powershell],
      associations,
    );
    const claims = result.trace_json!.claims;
    claims.push({ ...claims[0], claim_id: "A-02" });

    const context = buildTechnicalContext(result, sources);

    expect(context.status).toBe("retrieved_with_matches");
    expect(context.techniques.map((item) => item.techniqueId)).toEqual(["T1059.001"]);
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
    const trace = result.trace_json as Record<string, unknown>;
    const claims = trace.claims as Record<string, unknown>[];
    trace.claims = [claims[0], { ...claims[0], claim_id: "A-02" }];

    const context = buildTechnicalContext(result, sources);

    for (const technique of context.techniques) {
      const seen = technique.caseBasisSources.map((source) => `${source.id}|${source.exactQuote}`);
      expect(new Set(seen).size).toBe(seen.length);
    }
    expect(context.techniques[0].caseBasisSources[0].exactQuote).toBe(exactQuote);
  });
});

describe("mitreAttackUrl", () => {
  it("maps technique and sub-technique IDs to ATT&CK URLs", () => {
    expect(mitreAttackUrl("T1566")).toBe("https://attack.mitre.org/techniques/T1566/");
    expect(mitreAttackUrl("T1059.001")).toBe("https://attack.mitre.org/techniques/T1059/001/");
  });

  it("maps tactics, groups, software and other prefixes", () => {
    expect(mitreAttackUrl("TA0001")).toBe("https://attack.mitre.org/tactics/TA0001/");
    expect(mitreAttackUrl("G0001")).toBe("https://attack.mitre.org/groups/G0001/");
    expect(mitreAttackUrl("S0001")).toBe("https://attack.mitre.org/software/S0001/");
  });

  it("prioritizes customUrl when provided", () => {
    expect(mitreAttackUrl("T1059", "https://attack.mitre.org/techniques/T1059/custom/")).toBe(
      "https://attack.mitre.org/techniques/T1059/custom/",
    );
  });

  it("falls back gracefully for empty inputs", () => {
    expect(mitreAttackUrl("")).toBe("https://attack.mitre.org/");
  });
});
