import { fireEvent, render, screen } from "@testing-library/react";
import type { ComponentProps } from "react";
import { describe, expect, it, vi } from "vitest";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
import type { CaseAnalysisResultRead, CaseClarificationRead, CaseRunRead, EvidenceSourceRead } from "@/lib/api";
import { mockNativeDialog } from "./mock-native-dialog";

mockNativeDialog();

const caseId = "22222222-2222-4222-8222-222222222222";
const sourceId = "11111111-1111-4111-8111-111111111111";
const analysisId = "44444444-4444-4444-8444-444444444444";

function caseProjection(options: { technical?: boolean; page?: boolean; stale?: boolean } = {}): { result: CaseAnalysisResultRead; evidenceSources: EvidenceSourceRead[] } {
  const text = options.page ? "Page 4: received 52,000 baht." : "The reporting party named Account A.";
  const exactQuote = options.page ? "received 52,000 baht" : text;
  const evidenceSources: EvidenceSourceRead[] = [{
    id: sourceId,
    case_id: caseId,
    source_kind: options.page ? "reviewed_document" : "narrative",
    document_id: options.page ? "DOC-1" : null,
    origin_message_id: null,
    exact_text: text,
    provenance_json: options.page ? { pages: [{ end_offset: text.length, page_number: 4, start_offset: 0 }] } : { origin: "analyst-authored" },
    source_metadata_json: options.page ? { filename: "statement.pdf" } : {},
    created_at: "2026-09-10T00:00:00Z",
    archived_at: null,
  }];
  const locator = options.page ? { document_id: "DOC-1", filename: "statement.pdf", page_numbers: [4] } : {};
  const result: CaseAnalysisResultRead = {
    id: analysisId,
    case_id: caseId,
    run_id: "55555555-5555-4555-8555-555555555555",
    evidence_revision: 1,
    schema_version: "case_analysis_trace_v1",
    status: "validated",
    answer: text,
    summary: "The submitted material establishes a reported transaction.",
    trace_json: {
      version: "case_analysis_trace_v1",
      validation_status: "validated",
      analysis_mode: "case_overview",
      summary: "The submitted material establishes a reported transaction.",
      claims: [{
        claim_id: "A-01",
        claim_type: "reported",
        text: "The submitted material reports a transaction.",
        epistemic_status: "reported",
        reasoning_summary: null,
        supporting_source_ids: [sourceId],
        contradicting_source_ids: [],
        supporting_citations: [{ source_id: sourceId, exact_quote: exactQuote, ...locator }],
        contradicting_citations: [],
      }],
      gaps: [{ gap_id: "G-01", topic: "Incident time", status: "NOT_PROVIDED", description: "The incident time is missing.", affected_claim_ids: ["A-01"], reason: "Timing affects chronology.", priority: "high", askable: true }],
      mitre_associations: options.technical ? [{ association_id: "MA-01", technique_id: "T1059.001", claim_ids: ["A-01"], reason: "The evidence describes PowerShell activity.", status: "candidate_only", support_role: "external_technical_context" }] : [],
      retrieval_context_id: options.technical ? "retrieval-1" : null,
    },
    execution_receipt_json: {},
    retrieval_context_id: options.technical ? "retrieval-1" : null,
    pipeline_config: {},
    provider_metadata_json: options.technical ? {} : { technical_augmentation: { status: "not_applicable" } },
    created_at: "2026-09-10T00:00:00Z",
    freshness: options.stale ? "stale" : "current",
  };
  return { result, evidenceSources };
}

function renderOverview(overrides: Partial<ComponentProps<typeof CaseOverviewView>> = {}) {
  const projection = caseProjection();
  const props: ComponentProps<typeof CaseOverviewView> = {
    caseId,
    caseTitle: "Transfer Review",
    chatStatus: "answered",
    onOpenChat: vi.fn(),
    onOpenReport: vi.fn(),
    analysisResult: projection.result,
    evidenceSources: projection.evidenceSources,
    runStatus: "completed",
    clarifications: [],
    analysisLoading: false,
    evidenceLoading: false,
    run: null,
    ...overrides,
  };
  render(<CaseOverviewView {...props} />);
  return props;
}

function failedRun(): CaseRunRead {
  return {
    id: "55555555-5555-4555-8555-555555555555",
    case_id: caseId,
    operation: "analysis",
    evidence_revision: 1,
    request_message_id: null,
    status: "failed",
    attempt_count: 1,
    error_code: "analysis_failed",
    error_message: "Case analysis extraction failed.",
    created_at: "2026-09-10T00:00:00Z",
    started_at: "2026-09-10T00:00:01Z",
    finished_at: "2026-09-10T00:00:02Z",
    updated_at: "2026-09-10T00:00:02Z",
  };
}

describe("CaseOverviewView", () => {
  it("renders the empty Case state without a selected Case", () => {
    const openIntake = vi.fn();
    renderOverview({ caseId: null, analysisResult: null, evidenceSources: [], runStatus: null, onOpenIntake: openIntake });
    expect(screen.getByText("No Case Material Yet")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Open Intake" }));
    expect(openIntake).toHaveBeenCalledOnce();
  });

  it("renders the canonical Case projection and opens exact page evidence", () => {
    const projection = caseProjection({ page: true });
    const navigateToSource = vi.fn();
    renderOverview({ analysisResult: projection.result, evidenceSources: projection.evidenceSources, onNavigateToSource: navigateToSource });
    expect(screen.getByRole("heading", { name: /Executive Summary/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Case Findings/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Open Questions/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Source · statement.pdf · p. 4" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("received 52,000 baht");
    expect(screen.getByRole("dialog").querySelector("mark")).toHaveTextContent("received 52,000 baht");
    fireEvent.click(screen.getByRole("button", { name: /View in Materials/i }));
    expect(navigateToSource).toHaveBeenCalledWith(sourceId);
  });

  it("shows technical context only when the Case projection contains an association", () => {
    const nonTechnical = caseProjection();
    const { unmount } = render(<CaseOverviewView {...renderProps(nonTechnical.result, nonTechnical.evidenceSources)} />);
    expect(screen.queryByText(/MITRE ATT&CK/i)).not.toBeInTheDocument();
    unmount();
    const technical = caseProjection({ technical: true });
    render(<CaseOverviewView {...renderProps(technical.result, technical.evidenceSources)} />);
    expect(screen.getByRole("heading", { name: /External Cyber Reference/i })).toBeInTheDocument();
    expect(screen.getAllByText(/T1059.001/).length).toBeGreaterThan(0);
  });

  it("renders the failed run state without an analysis result", () => {
    const openIntake = vi.fn();
    renderOverview({ analysisResult: null, evidenceSources: [], runStatus: "failed", run: failedRun(), onOpenIntake: openIntake });
    expect(screen.getByText("Analysis Failed")).toBeInTheDocument();
    expect(screen.getByText("Case analysis extraction failed.")).toBeInTheDocument();
  });

  it("routes a pending clarification to Chat", () => {
    const openChat = vi.fn();
    const clarification: CaseClarificationRead = {
      id: "66666666-6666-4666-8666-666666666666",
      case_id: caseId,
      origin_analysis_result_id: analysisId,
      gap_key: "topic:incident-time",
      gap_id: "G-01",
      topic: "Incident time",
      question: "When did the incident occur?",
      metadata_json: {},
      state: "pending",
      answer_evidence_source_id: null,
      question_message_id: null,
      answer_message_id: null,
      answer_fingerprint: null,
      answered_at: null,
      created_at: "2026-09-10T01:00:00Z",
      updated_at: "2026-09-10T01:00:00Z",
    };
    renderOverview({ chatStatus: "awaiting_followup", clarifications: [clarification], onOpenChat: openChat });
    expect(screen.getByText("Analysis Needs More Information")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Proceed to Chat" }));
    expect(openChat).toHaveBeenCalledOnce();
  });

  it("offers reanalysis when the canonical result is stale", () => {
    const projection = caseProjection({ stale: true });
    const runAnalysis = vi.fn();
    renderOverview({ analysisResult: projection.result, evidenceSources: projection.evidenceSources, onRunAnalysis: runAnalysis });
    expect(screen.getByText(/Analysis is based on older evidence/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Analyze latest evidence/i }));
    expect(runAnalysis).toHaveBeenCalledOnce();
  });
});

function renderProps(result: CaseAnalysisResultRead, evidenceSources: EvidenceSourceRead[]): ComponentProps<typeof CaseOverviewView> {
  return {
    caseId,
    caseTitle: "Transfer Review",
    chatStatus: "answered",
    onOpenChat: vi.fn(),
    onOpenReport: vi.fn(),
    analysisResult: result,
    evidenceSources,
    runStatus: "completed",
    clarifications: [],
    analysisLoading: false,
    evidenceLoading: false,
    run: null,
  };
}
