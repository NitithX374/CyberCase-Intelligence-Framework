import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
import type { CaseAnalysisResultRead, CaseFollowUpRead, CaseRunRead, CaseSourceRead } from "@/lib/api";
import {
  useCase,
  useCaseAnalysis,
  useCaseEvidence,
  useCaseFollowUps,
  useCaseRunState,
  useStartCaseAnalysis,
} from "@/hooks/useCaseQueries";
import { mockNativeDialog } from "./mock-native-dialog";

mockNativeDialog();

const routerPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: routerPush }),
}));

vi.mock("@/hooks/useCaseQueries", () => ({
  useCase: vi.fn(),
  useCaseAnalysis: vi.fn(),
  useCaseEvidence: vi.fn(),
  useCaseFollowUps: vi.fn(),
  caseProcessingStatus: vi.fn(),
  useCaseRunState: vi.fn(),
  useStartCaseAnalysis: vi.fn(),
}));

const caseId = "22222222-2222-4222-8222-222222222222";
const sourceId = "11111111-1111-4111-8111-111111111111";
const analysisId = "44444444-4444-4444-8444-444444444444";

function caseProjection(options: { technical?: boolean; rag?: boolean; page?: boolean; stale?: boolean } = {}): { result: CaseAnalysisResultRead; evidenceSources: CaseSourceRead[] } {
  const text = options.page ? "Page 4: received 52,000 baht." : "The reporting party named Account A.";
  const exactQuote = options.page ? "received 52,000 baht" : text;
  const evidenceSources: CaseSourceRead[] = [{
    id: sourceId,
    case_id: caseId,
    source_kind: options.page ? "document" : "narrative",
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
      retrieval_context_id: options.technical || options.rag ? "retrieval-1" : null,
    },
    execution_receipt_json: {},
    retrieval_context_id: options.technical ? "retrieval-1" : null,
    pipeline_config: {},
    external_context_json: options.rag
      ? {
          technical_augmentation: {
            version: "case_mitre_augmentation_v1",
            status: "retrieved_from_rag",
            applicability: { decision: "RETRIEVE", source_message_ids: [sourceId], trigger_text: [text] },
            retrieval_context_id: "retrieval-1",
            mitre_table: [
              { technique_id: "T1059.001", name: "PowerShell", tactic: "Execution", description: "Command and scripting interpreter." },
              { technique_id: "S0096", name: "Systeminfo", entity_type: "Software", tactic: "", description: "System information utility." },
            ],
            association_ids: [],
          },
        }
      : options.technical ? {} : { technical_augmentation: { status: "not_applicable" } },
    created_at: "2026-09-10T00:00:00Z",
    freshness: options.stale ? "stale" : "current",
  };
  return { result, evidenceSources };
}

function failedRun(): CaseRunRead {
  return {
    id: "55555555-5555-4555-8555-555555555555",
    case_id: caseId,
    evidence_revision: 1,
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

interface MockOverrides {
  caseId?: string | null;
  caseTitle?: string;
  chatStatus?: string;
  analysisResult?: CaseAnalysisResultRead | null;
  evidenceSources?: CaseSourceRead[];
  runStatus?: string | null;
  run?: CaseRunRead | null;
  followups?: CaseFollowUpRead[];
  analysisLoading?: boolean;
  evidenceLoading?: boolean;
}

function configureAndRender(overrides: MockOverrides = {}) {
  const id = overrides.caseId === undefined ? caseId : overrides.caseId;
  const projection = caseProjection();
  const result = overrides.analysisResult !== undefined ? overrides.analysisResult : projection.result;
  const evidence = overrides.evidenceSources !== undefined ? overrides.evidenceSources : projection.evidenceSources;
  const followups = overrides.followups ?? [];
  const run = overrides.run ?? null;
  const runStatus = overrides.runStatus !== undefined ? overrides.runStatus : "completed";
  const chatStatus = overrides.chatStatus ?? "answered";

  vi.mocked(useCase).mockReturnValue({
    data: id ? {
      id,
      user_id: "user-1",
      title: overrides.caseTitle ?? "Transfer Review",
      status: chatStatus,
      evidence_revision: result?.evidence_revision ?? 1,
      latest_analysis_result_id: result?.id ?? null,
      active_run_id: runStatus === "queued" || runStatus === "running" ? run?.id ?? null : null,
      latest_run_id: run?.id ?? null,
      processing_status: runStatus ?? "idle",
      has_pending_followup: followups.some((f) => f.state === "pending"),
      analysis_freshness: result?.freshness ?? "current",
      created_at: "2026-09-10T00:00:00Z",
      updated_at: "2026-09-14T00:00:00Z",
    } : undefined,
    isLoading: false,
  } as never);

  vi.mocked(useCaseAnalysis).mockReturnValue({
    data: result,
    isLoading: overrides.analysisLoading ?? false,
  } as never);

  vi.mocked(useCaseEvidence).mockReturnValue({
    data: evidence,
    isLoading: overrides.evidenceLoading ?? false,
  } as never);

  vi.mocked(useCaseFollowUps).mockReturnValue({
    data: followups,
    isLoading: false,
  } as never);

  vi.mocked(useCaseRunState).mockReturnValue({
    data: run ? { ...run, status: runStatus ?? run.status } : undefined,
    isLoading: false,
  } as never);

  vi.mocked(useStartCaseAnalysis).mockReturnValue({
    isPending: false,
    mutateAsync: vi.fn(),
  } as never);

  render(<CaseOverviewView caseId={id} />);
}

beforeEach(() => {
  routerPush.mockClear();
});

describe("CaseOverviewView", () => {
  it("renders the empty Case state without a selected Case", () => {
    configureAndRender({ caseId: null, analysisResult: null, evidenceSources: [], runStatus: null });
    expect(screen.getByText("No Case Material Yet")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Open Intake" }));
    expect(routerPush).toHaveBeenCalledOnce();
  });

  it("renders the canonical Case projection and opens exact page evidence", () => {
    const projection = caseProjection({ page: true });
    configureAndRender({ analysisResult: projection.result, evidenceSources: projection.evidenceSources });
    expect(screen.getByRole("heading", { name: /Executive Summary/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Case Findings/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Open Questions/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Source · statement.pdf · p. 4" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("received 52,000 baht");
    expect(screen.getByRole("dialog").querySelector("mark")).toHaveTextContent("received 52,000 baht");
    fireEvent.click(screen.getByRole("button", { name: /View in Materials/i }));
    expect(routerPush).toHaveBeenCalled();
  });

  it("does not render external cyber references in the Case Overview", () => {
    const technical = caseProjection({ technical: true, rag: true });
    configureAndRender({ analysisResult: technical.result, evidenceSources: technical.evidenceSources });
    expect(screen.queryByRole("heading", { name: /External Cyber Reference/i })).not.toBeInTheDocument();
    expect(screen.queryByText(/External cyber reference unavailable/i)).not.toBeInTheDocument();
  });

  it("renders the failed run state without an analysis result", () => {
    configureAndRender({ analysisResult: null, evidenceSources: [], runStatus: "failed", run: failedRun() });
    expect(screen.getByText("Analysis Failed")).toBeInTheDocument();
    expect(screen.getByText("Case analysis extraction failed.")).toBeInTheDocument();
  });

  it("shows the pending follow-up from the Case analysis", () => {
    const followup: CaseFollowUpRead = {
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
    configureAndRender({ chatStatus: "awaiting_followup", followups: [followup] });
    expect(screen.getByText(/Analysis Needs More Information/i)).toBeInTheDocument();
    expect(screen.getByText(/Respond in the Ask panel on the right/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Executive Summary/i })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Proceed to Chat" })).not.toBeInTheDocument();
  });

  it("offers reanalysis when the canonical result is stale", () => {
    const projection = caseProjection({ stale: true });
    configureAndRender({ analysisResult: projection.result, evidenceSources: projection.evidenceSources });
    expect(screen.getByText(/Analysis is based on older evidence/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Analyze latest evidence/i })).toBeInTheDocument();
  });

  it("switches between Case Findings and Open Questions tabs", () => {
    const projection = caseProjection();
    configureAndRender({ analysisResult: projection.result, evidenceSources: projection.evidenceSources });

    const findingsTab = screen.getByRole("tab", { name: /Case Findings/i });
    const questionsTab = screen.getByRole("tab", { name: /Open Questions/i });

    expect(findingsTab).toHaveAttribute("aria-selected", "true");
    expect(questionsTab).toHaveAttribute("aria-selected", "false");

    const findingsPanel = document.getElementById("panel-findings");
    const questionsPanel = document.getElementById("panel-questions");
    expect(findingsPanel).toHaveClass("block");
    expect(questionsPanel).toHaveClass("hidden");

    fireEvent.click(questionsTab);

    expect(findingsTab).toHaveAttribute("aria-selected", "false");
    expect(questionsTab).toHaveAttribute("aria-selected", "true");
    expect(findingsPanel).toHaveClass("hidden");
    expect(questionsPanel).toHaveClass("block");
  });
});
