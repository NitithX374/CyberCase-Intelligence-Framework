import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TechnicalContextView } from "@/components/technical/TechnicalContextView";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead } from "@/lib/api";
import { sha256Hex } from "@/lib/sha256";
import { mockNativeDialog } from "../overview/mock-native-dialog";

mockNativeDialog();

const caseId = "22222222-2222-4222-8222-222222222222";
const sourceId = "11111111-1111-4111-8111-111111111111";
const snapshotId = "33333333-3333-4333-8333-333333333333";
const exactQuote = "The evidence reports PowerShell network activity.";

function technicalProjection(): {
  result: CaseAnalysisResultRead;
  snapshot: CaseEvidenceSnapshotRead;
} {
  const manifest = [{
    exact_text: exactQuote,
    provenance: { origin: "analyst-authored" },
    revision: 1,
    source_id: sourceId,
    source_kind: "narrative",
    text_sha256: sha256Hex(exactQuote),
  }];
  const snapshot: CaseEvidenceSnapshotRead = {
    id: snapshotId,
    case_id: caseId,
    evidence_revision: 1,
    format_version: "case_evidence_snapshot_v1",
    manifest_json: manifest,
    input_text: exactQuote,
    text_sha256: sha256Hex(exactQuote),
    manifest_sha256: sha256Hex(JSON.stringify(manifest)),
    created_at: "2026-09-10T00:00:00Z",
  };
  const result: CaseAnalysisResultRead = {
    id: "44444444-4444-4444-8444-444444444444",
    case_id: caseId,
    run_id: "55555555-5555-4555-8555-555555555555",
    snapshot_id: snapshotId,
    schema_version: "case_analysis_result_v1",
    status: "validated",
    answer: exactQuote,
    summary: exactQuote,
    trace_json: {
      version: "case_analysis_trace_v1",
      validation_status: "validated",
      analysis_mode: "case_overview",
      evidence_sha256: snapshot.text_sha256,
      summary: exactQuote,
      claims: [{
        claim_id: "A-01",
        claim_type: "reported",
        text: exactQuote,
        epistemic_status: "reported",
        reasoning_summary: null,
        supporting_source_ids: [sourceId],
        contradicting_source_ids: [],
        supporting_citations: [{ source_id: sourceId, source_revision: 1, exact_quote: exactQuote }],
        contradicting_citations: [],
      }],
      gaps: [],
      mitre_associations: [{
        association_id: "MA-01",
        technique_id: "T1059.001",
        claim_ids: ["A-01"],
        reason: "The claim describes PowerShell activity.",
        status: "candidate_only",
        support_role: "external_technical_context",
      }],
      retrieval_context_id: "retrieval-1",
    },
    execution_receipt_json: {},
    retrieval_context_id: "retrieval-1",
    pipeline_config: {},
    provider_metadata_json: {
      technical_augmentation: {
        version: "case_mitre_augmentation_v1",
        status: "retrieved_with_matches",
        applicability: { decision: "RETRIEVE", source_message_ids: [sourceId], trigger_text: [exactQuote] },
        retrieval_context_id: "retrieval-1",
        mitre_table: [{ technique_id: "T1059.001", name: "PowerShell", tactic: "Execution", description: "Command and scripting interpreter." }],
        query_sha256: "a".repeat(64),
        association_ids: ["MA-01"],
      },
    },
    created_at: "2026-09-10T00:00:00Z",
    freshness: "current",
  };
  return { result, snapshot };
}

describe("TechnicalContextView", () => {
  it("shows the optional-context empty state without Case analysis", () => {
    const openIntake = vi.fn();
    render(<TechnicalContextView analysisResult={null} evidenceSnapshot={null} onOpenIntake={openIntake} />);
    expect(screen.getByText("Technical augmentation outcome is unavailable")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Go to Intake/i }));
    expect(openIntake).toHaveBeenCalledOnce();
  });

  it("shows validated Case mappings and inspects their exact source", () => {
    const projection = technicalProjection();
    const navigateToSource = vi.fn();
    render(<TechnicalContextView analysisResult={projection.result} evidenceSnapshot={projection.snapshot} onNavigateToSource={navigateToSource} />);
    expect(screen.getByText("Validated Case mappings")).toBeInTheDocument();
    expect(screen.getByText("PowerShell")).toBeInTheDocument();
    const source = screen.getByRole("button", { name: /Source — Source .* revision 1/i });
    fireEvent.click(source);
    expect(screen.getByRole("dialog")).toHaveTextContent(exactQuote);
    fireEvent.click(screen.getByRole("button", { name: /View in Materials/i }));
    expect(navigateToSource).toHaveBeenCalledWith(sourceId);
  });

  it("keeps a non-technical Case valid without MITRE rows", () => {
    const projection = technicalProjection();
    projection.result.trace_json = {
      ...projection.result.trace_json,
      mitre_associations: [],
      retrieval_context_id: null,
    };
    projection.result.retrieval_context_id = null;
    projection.result.provider_metadata_json = {
      technical_augmentation: {
        version: "case_mitre_augmentation_v1",
        status: "not_applicable",
        applicability: { decision: "SKIP", source_message_ids: [], trigger_text: [] },
        retrieval_context_id: null,
        mitre_table: [],
        query_sha256: null,
        association_ids: [],
      },
    };
    render(<TechnicalContextView analysisResult={projection.result} evidenceSnapshot={projection.snapshot} />);
    expect(screen.getByText("MITRE augmentation was not applicable")).toBeInTheDocument();
    expect(screen.queryByText("PowerShell")).not.toBeInTheDocument();
  });
});
