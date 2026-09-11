import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TechnicalContextView } from "@/components/technical/TechnicalContextView";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead, PersistedChatMessage } from "@/lib/api";
import { sha256Hex } from "@/lib/sha256";

describe("TechnicalContextView", () => {
  const sampleMessages: PersistedChatMessage[] = [
    {
      id: "msg-1",
      thread_id: "thread-1",
      ordinal: 1,
      role: "user",
      content: "คนร้ายเจาะระบบผ่านช่องโหว่ IIS Web Server",
      retrieval_context_id: null,
      metadata_json: {},
      created_at: "2026-03-10T08:00:00Z",
    },
    {
      id: "msg-2",
      thread_id: "thread-1",
      ordinal: 2,
      role: "assistant",
      content: "วิเคราะห์...",
      retrieval_context_id: "ret-1",
      metadata_json: {
        analysis_kind: "grounded_main_analysis",
        mitre_table: [
          {
            technique_id: "T1190",
            name: "Exploit Public-Facing Application",
            tactic: "Initial Access",
            description: "Abuse of a public-facing application to gain access.",
            reason: "คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server",
          },
        ],
        analysis_trace: {
          version: "analysis_trace_v2",
          claims: [
            {
              claim_id: "c1",
              text: "คนร้ายโจมตีผ่านช่องโหว่ IIS",
              claim_type: "event_progression",
              epistemic_status: "reported",
              source_message_ids: ["msg-1"],
            },
          ],
          mitre_associations: [
            {
              association_id: "assoc-1",
              technique_id: "T1190",
              claim_ids: ["c1"],
              reason: "คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server",
              status: "candidate",
              support_role: "external_knowledge",
            },
          ],
        },
      },
      created_at: "2026-03-10T08:01:00Z",
    },
  ];

  it("renders flattened MITRE notes with quiet external reference notice and case basis", () => {
    render(<TechnicalContextView messages={sampleMessages} />);

    expect(screen.getByText("MITRE ATT&CK Context")).toBeInTheDocument();
    expect(screen.getByText("External technical reference · not case evidence")).toBeInTheDocument();

    // Technique details
    expect(screen.getByText("T1190")).toBeInTheDocument();
    expect(screen.getByText("Exploit Public-Facing Application")).toBeInTheDocument();
    expect(screen.getByText("Initial Access")).toBeInTheDocument();
    expect(screen.getByText("ความหมายโดยย่อ")).toBeInTheDocument();
    expect(screen.getByText("เหตุผลการเชื่อมโยงเชิงวิเคราะห์")).toBeInTheDocument();
    expect(screen.getByText("คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server")).toBeInTheDocument();

    // Case basis source button
    const sourceBtn = screen.getByRole("button", { name: /Source — Initial case description/i });
    expect(sourceBtn).toBeInTheDocument();

    // Click source button to open popover
    fireEvent.click(sourceBtn);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText(/SOURCE FROM CASE/i)).toBeInTheDocument();
    expect(screen.getByText("คนร้ายเจาะระบบผ่านช่องโหว่ IIS Web Server")).toBeInTheDocument();
  });

  it("renders empty state when no MITRE context exists", () => {
    render(<TechnicalContextView messages={[]} />);
    expect(
      screen.getByText(/No relevant MITRE ATT&CK context is currently available/i),
    ).toBeInTheDocument();
  });

  const sourceId = "11111111-1111-4111-8111-111111111111";
  const caseId = "22222222-2222-4222-8222-222222222222";
  const snapshotId = "33333333-3333-4333-8333-333333333333";
  const quote = "The evidence reports PowerShell network activity.";

  function nativeFixture(
    status: string,
    rows: Record<string, string>[],
    associations: Array<{ association_id: string; technique_id: string; claim_ids: string[]; reason: string }> = [],
    invalidTrace = false,
  ): { result: CaseAnalysisResultRead; snapshot: CaseEvidenceSnapshotRead } {
    const manifest = [{
      exact_text: quote,
      provenance: { origin: "analyst-authored" },
      revision: 1,
      source_id: sourceId,
      source_kind: "narrative",
      text_sha256: sha256Hex(quote),
    }];
    const snapshot: CaseEvidenceSnapshotRead = {
      id: snapshotId,
      case_id: caseId,
      evidence_revision: 1,
      format_version: "case_evidence_snapshot_v1",
      manifest_json: manifest,
      input_text: quote,
      text_sha256: sha256Hex(quote),
      manifest_sha256: sha256Hex(JSON.stringify(manifest)),
      created_at: "2026-09-10T00:00:00Z",
    };
    const retrievalContextId = status === "not_applicable" ? null : "retrieval-native-1";
    const traceAssociations = associations.map((association) => ({
      association_id: association.association_id,
      technique_id: association.technique_id,
      claim_ids: association.claim_ids,
      reason: association.reason,
      status: "candidate_only",
      support_role: "external_technical_context",
    }));
    const result: CaseAnalysisResultRead = {
      id: "44444444-4444-4444-8444-444444444444",
      case_id: caseId,
      run_id: "55555555-5555-4555-8555-555555555555",
      snapshot_id: snapshotId,
      schema_version: "case_analysis_result_v1",
      status: "validated",
      answer: quote,
      summary: quote,
      trace_json: {
        version: "case_analysis_trace_v1",
        validation_status: "validated",
        analysis_mode: "case_overview",
        evidence_sha256: invalidTrace ? "0".repeat(64) : snapshot.text_sha256,
        summary: quote,
        claims: [{
          claim_id: "A-01",
          claim_type: "reported",
          text: quote,
          epistemic_status: "reported",
          reasoning_summary: null,
          supporting_source_ids: [sourceId],
          contradicting_source_ids: [],
          supporting_citations: [{ source_id: sourceId, source_revision: 1, exact_quote: quote }],
          contradicting_citations: [],
        }],
        gaps: [],
        mitre_associations: traceAssociations,
        retrieval_context_id: retrievalContextId,
      },
      execution_receipt_json: {},
      retrieval_context_id: retrievalContextId,
      pipeline_config: {},
      provider_metadata_json: {
        technical_augmentation: {
          version: "case_mitre_augmentation_v1",
          status,
          applicability: { decision: "RETRIEVE", source_message_ids: [sourceId], trigger_text: [quote] },
          retrieval_context_id: retrievalContextId,
          mitre_table: rows,
          query_sha256: "a".repeat(64),
          association_ids: associations.map((association) => association.association_id),
          ...(status === "failed" ? { failure_code: "mitre_mapping_invalid" } : {}),
        },
      },
      created_at: "2026-09-10T00:00:00Z",
      freshness: "current",
    };
    return { result, snapshot };
  }

  it("renders mapping failure and keeps retrieved rows out of Case mappings", () => {
    const fixture = nativeFixture("failed", [{ technique_id: "T1059.001", name: "PowerShell", tactic: "Execution", description: "Command interpreter." }]);
    render(<TechnicalContextView messages={[]} nativeAnalysisResult={fixture.result} nativeEvidenceSnapshot={fixture.snapshot} />);
    expect(screen.getByText(/Technical augmentation failed during mapping/i)).toBeInTheDocument();
    expect(screen.getByText(/Retrieved-only technical context/i)).toBeInTheDocument();
    expect(screen.getByText(/Retrieved-only context · no validated Case mapping/i)).toBeInTheDocument();
    expect(screen.queryByText("Validated Case mappings")).not.toBeInTheDocument();
  });

  it("renders a no-supported-match outcome distinctly", () => {
    const fixture = nativeFixture("retrieved_without_supported_match", [{ technique_id: "T1018", name: "Remote System Discovery", tactic: "Discovery", description: "Discovery." }]);
    render(<TechnicalContextView messages={[]} nativeAnalysisResult={fixture.result} nativeEvidenceSnapshot={fixture.snapshot} />);
    expect(screen.getByText(/retrieved without a supported Case match/i)).toBeInTheDocument();
    expect(screen.queryByText("เหตุผลการเชื่อมโยงเชิงวิเคราะห์")).not.toBeInTheDocument();
  });

  it("renders empty retrieval as an explicit insufficient outcome", () => {
    const fixture = nativeFixture("insufficient_context", []);
    render(<TechnicalContextView messages={[]} nativeAnalysisResult={fixture.result} nativeEvidenceSnapshot={fixture.snapshot} />);
    expect(screen.getByText(/Technical context was insufficient/i)).toBeInTheDocument();
    expect(screen.queryByText(/No relevant MITRE ATT&CK context is currently available/i)).not.toBeInTheDocument();
  });

  it("renders partial mappings as validated and retrieved-only groups", () => {
    const fixture = nativeFixture(
      "retrieved_with_matches",
      [
        { technique_id: "T1059.001", name: "PowerShell", tactic: "Execution", description: "Command interpreter." },
        { technique_id: "T1105", name: "Ingress Tool Transfer", tactic: "Command and Control", description: "Tool transfer." },
      ],
      [{ association_id: "MA-01", technique_id: "T1059.001", claim_ids: ["A-01"], reason: "PowerShell is described." }],
    );
    render(<TechnicalContextView messages={[]} nativeAnalysisResult={fixture.result} nativeEvidenceSnapshot={fixture.snapshot} />);
    expect(screen.getByText("Validated Case mappings")).toBeInTheDocument();
    expect(screen.getByText("PowerShell")).toBeInTheDocument();
    expect(screen.getByText("Retrieved-only technical context")).toBeInTheDocument();
    expect(screen.getByText("Ingress Tool Transfer")).toBeInTheDocument();
  });

  it("renders invalid trace state instead of an ordinary empty state", () => {
    const fixture = nativeFixture("retrieved_without_supported_match", [], [], true);
    render(<TechnicalContextView messages={[]} nativeAnalysisResult={fixture.result} nativeEvidenceSnapshot={fixture.snapshot} />);
    expect(screen.getByText(/Saved technical trace is invalid/i)).toBeInTheDocument();
    expect(screen.getByText(/invalid_trace/i)).toBeInTheDocument();
    expect(screen.queryByText(/No relevant MITRE ATT&ACK context/i)).not.toBeInTheDocument();
  });
});
