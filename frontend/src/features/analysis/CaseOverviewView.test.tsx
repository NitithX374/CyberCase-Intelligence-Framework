import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { CaseOverviewView } from "./CaseOverviewView";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api";
import { useCase } from "@/features/cases/queries";
import { useCaseAnalysis, useIsCaseAnalysisRunning } from "@/features/analysis/queries";
import { useCaseSources } from "@/features/sources/queries";
import { useCaseChatMessages } from "@/features/chat/useCaseChat";
import { mockNativeDialog } from "@/test/mockNativeDialog";
import { WorkspaceActivityProvider } from "@/features/workspace/WorkspaceActivityContext";

mockNativeDialog();

const routerPush = vi.fn();
const runAnalysis = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: routerPush }),
}));

vi.mock("@/features/cases/queries", () => ({ useCase: vi.fn() }));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: vi.fn(),
  useIsCaseAnalysisRunning: vi.fn(),
}));
vi.mock("@/features/sources/queries", () => ({ useCaseSources: vi.fn() }));

vi.mock("@/features/chat/useCaseChat", () => ({
  useCaseChatMessages: vi.fn(),
}));

const caseId = "22222222-2222-4222-8222-222222222222";
const sourceId = "11111111-1111-4111-8111-111111111111";
const analysisId = "44444444-4444-4444-8444-444444444444";

function caseProjection(
  options: { technical?: boolean; rag?: boolean; page?: boolean; stale?: boolean } = {},
): { result: CaseAnalysisResultRead; sources: CaseSourceRead[] } {
  const text = options.page
    ? "Page 4: received 52,000 baht."
    : "The reporting party named Account A.";
  const exactQuote = options.page ? "received 52,000 baht" : text;
  const sources: CaseSourceRead[] = [
    {
      id: sourceId,
      case_id: caseId,
      source_kind: options.page ? "document" : "narrative",
      document_id: options.page ? "DOC-1" : null,
      filename: options.page ? "statement.pdf" : null,
      exact_text: text,
      provenance_json: options.page
        ? { pages: [{ end_offset: text.length, page_number: 4, start_offset: 0 }] }
        : { origin: "analyst-authored" },
      source_metadata_json: {},
      created_at: "2026-09-10T00:00:00Z",
      archived_at: null,
    },
  ];
  const locator = options.page
    ? { document_id: "DOC-1", filename: "statement.pdf", page_numbers: [4] }
    : {};
  const result: CaseAnalysisResultRead = {
    id: analysisId,
    case_id: caseId,
    source_revision: 1,
    schema_version: "case_analysis_trace_v1",
    status: "validated",
    summary: "The submitted material establishes a reported transaction.",
    trace_json: {
      version: "case_analysis_trace_v1",
      validation_status: "validated",
      analysis_mode: "case_overview",
      summary: "The submitted material establishes a reported transaction.",
      claims: [
        {
          claim_id: "A-01",
          claim_type: "reported",
          text: "The submitted material reports a transaction.",
          epistemic_status: "reported",
          reasoning_summary: null,
          supporting_source_ids: [sourceId],
          contradicting_source_ids: [],
          supporting_citations: [{ source_id: sourceId, exact_quote: exactQuote, ...locator }],
          contradicting_citations: [],
        },
      ],
      gaps: [
        {
          gap_id: "G-01",
          gap_key: "topic:incident-time",
          topic: "Incident time",
          status: "NOT_PROVIDED",
          description: "The incident time is missing.",
          affected_claim_ids: ["A-01"],
          reason: "Timing affects chronology.",
          priority: "high",
          askable: true,
          clarification_question: "When did the incident occur?",
        },
      ],
      mitre_associations: options.technical
        ? [
            {
              association_id: "MA-01",
              technique_id: "T1059.001",
              claim_ids: ["A-01"],
              reason: "The source describes PowerShell activity.",
              plain_meaning: "Someone ran commands through PowerShell.",
              status: "candidate_only",
              support_role: "external_technical_context",
            },
          ]
        : [],
      retrieval_context_id: options.technical || options.rag ? "retrieval-1" : null,
    },
    retrieval_context_id: options.technical ? "retrieval-1" : null,
    pipeline_config: {},
    external_context_json: options.rag
      ? {
          technical_augmentation: {
            version: "case_mitre_augmentation_v1",
            status: "retrieved_from_rag",
            applicability: {
              decision: "RETRIEVE",
              source_message_ids: [sourceId],
              trigger_text: [text],
            },
            retrieval_context_id: "retrieval-1",
            mitre_table: [
              {
                technique_id: "T1059.001",
                name: "PowerShell",
                tactic: "Execution",
                description: "Command and scripting interpreter.",
              },
              {
                technique_id: "S0096",
                name: "Systeminfo",
                entity_type: "Software",
                tactic: "",
                description: "System information utility.",
              },
            ],
            association_ids: [],
          },
        }
      : options.technical
        ? {}
        : { technical_augmentation: { status: "not_applicable" } },
    created_at: "2026-09-10T00:00:00Z",
    freshness: options.stale ? "stale" : "current",
  };
  return { result, sources };
}

interface MockOverrides {
  caseId?: string | null;
  caseTitle?: string;
  chatStatus?: string;
  analysisResult?: CaseAnalysisResultRead | null;
  sources?: CaseSourceRead[];
  analysisLoading?: boolean;
  sourcesLoading?: boolean;
  followupPending?: boolean;
  analysisRunning?: boolean;
}

function configureAndRender(overrides: MockOverrides = {}) {
  const id = overrides.caseId === undefined ? caseId : overrides.caseId;
  const projection = caseProjection();
  const result =
    overrides.analysisResult !== undefined ? overrides.analysisResult : projection.result;
  const sourceRows = overrides.sources !== undefined ? overrides.sources : projection.sources;
  const chatStatus = overrides.chatStatus ?? "answered";

  vi.mocked(useCase).mockReturnValue({
    data: id
      ? {
          id,
          user_id: "user-1",
          title: overrides.caseTitle ?? "Transfer Review",
          status: chatStatus,
          source_revision: result?.source_revision ?? 1,
          latest_analysis_result_id: result?.id ?? null,
          analysis_freshness: result?.freshness ?? "current",
          created_at: "2026-09-10T00:00:00Z",
          updated_at: "2026-09-14T00:00:00Z",
        }
      : undefined,
    isLoading: false,
  } as never);

  vi.mocked(useCaseAnalysis).mockReturnValue({
    data: result,
    isLoading: overrides.analysisLoading ?? false,
  } as never);

  vi.mocked(useCaseSources).mockReturnValue({
    data: sourceRows,
    isLoading: overrides.sourcesLoading ?? false,
  } as never);

  vi.mocked(useCaseChatMessages).mockReturnValue({
    data: { case_id: id ?? "none", status: "answered", messages: [] },
    isLoading: false,
  } as never);

  vi.mocked(useIsCaseAnalysisRunning).mockReturnValue(overrides.analysisRunning ?? false);

  render(
    <WorkspaceActivityProvider
      isFollowupPending={overrides.followupPending ?? false}
      runAnalysis={runAnalysis}
    >
      <CaseOverviewView caseId={id} />
    </WorkspaceActivityProvider>,
  );
}

beforeEach(() => {
  routerPush.mockClear();
  runAnalysis.mockClear();
});

describe("CaseOverviewView", () => {
  it("renders the empty Case state without a selected Case", () => {
    configureAndRender({ caseId: null, analysisResult: null, sources: [] });
    expect(screen.getByText("No case material yet")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Open sources" })).not.toBeInTheDocument();
  });

  it("renders the canonical Case projection and opens the exact page", () => {
    const projection = caseProjection({ page: true });
    configureAndRender({ analysisResult: projection.result, sources: projection.sources });
    expect(screen.getByRole("heading", { name: "Summary" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Findings/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Open questions/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "statement.pdf · p. 4" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("received 52,000 baht");
    expect(screen.getByRole("dialog").querySelector("mark")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Open in Sources/i }));
    expect(routerPush).toHaveBeenCalled();
  });

  it("does not render external cyber references in the Case Overview", () => {
    const technical = caseProjection({ technical: true, rag: true });
    configureAndRender({ analysisResult: technical.result, sources: technical.sources });
    expect(
      screen.queryByRole("heading", { name: /External Cyber Reference/i }),
    ).not.toBeInTheDocument();
    expect(screen.queryByText(/External cyber reference unavailable/i)).not.toBeInTheDocument();
  });

  it("offers reanalysis when the canonical result is stale", () => {
    const projection = caseProjection({ stale: true });
    configureAndRender({ analysisResult: projection.result, sources: projection.sources });
    expect(screen.getByText(/Analysis is based on older sources/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Analyze again" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Analyze latest sources/i }));
    expect(runAnalysis).toHaveBeenCalledOnce();
  });

  it("offers to run an up-to-date analysis again beside its status", () => {
    const projection = caseProjection();
    configureAndRender({ analysisResult: projection.result, sources: projection.sources });

    fireEvent.click(screen.getByRole("button", { name: "Analyze again" }));
    expect(runAnalysis).toHaveBeenCalledOnce();
  });

  it("names the case's files in the analysis record", () => {
    const projection = caseProjection({ page: true });
    configureAndRender({ analysisResult: projection.result, sources: projection.sources });

    fireEvent.click(screen.getByRole("button", { name: "Analysis record" }));
    expect(screen.getByText("Documents").nextElementSibling).toHaveTextContent("statement.pdf");
  });

  it("says the analysis is being updated while a run is in flight", () => {
    const projection = caseProjection();
    configureAndRender({
      analysisResult: projection.result,
      sources: projection.sources,
      analysisRunning: true,
    });

    expect(screen.getByRole("status")).toHaveTextContent("Updating the case analysis…");
    expect(screen.queryByRole("button", { name: "Analyze again" })).not.toBeInTheDocument();
  });

  it("shows progress while Chat applies a follow-up answer", () => {
    const projection = caseProjection({ stale: true });
    configureAndRender({
      analysisResult: projection.result,
      sources: projection.sources,
      followupPending: true,
    });

    expect(screen.getByRole("status")).toHaveTextContent("Updating the case analysis");
    expect(
      screen.queryByRole("button", { name: /Analyze latest sources/i }),
    ).not.toBeInTheDocument();
  });

  it("offers to analyze a case that has sources but no analysis yet", () => {
    const projection = caseProjection();
    configureAndRender({ analysisResult: null, sources: projection.sources });

    expect(screen.getByRole("heading", { name: "Not analyzed yet" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    expect(runAnalysis).toHaveBeenCalledOnce();
  });

  it("switches between the Findings and Open questions tabs", () => {
    const projection = caseProjection();
    configureAndRender({ analysisResult: projection.result, sources: projection.sources });

    const findingsTab = screen.getByRole("tab", { name: /Findings/i });
    const questionsTab = screen.getByRole("tab", { name: /Open questions/i });

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
