import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { AnalysisLayout } from "@/features/analysis/AnalysisLayout";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api/types";
import { useCaseAnalysis, useIsCaseAnalysisRunning } from "@/features/analysis/queries";
import { useCaseSources } from "@/features/sources/queries";
import { useIsFollowupPending } from "@/features/chat/useCaseChat";
import {
  analysisResult,
  caseId,
  claim,
  followupHistory,
  narrativeSource,
  pagedDocumentSource,
  sourcesRead,
  trace,
} from "@/test/fixtures";

const state = vi.hoisted(() => ({
  routerPush: vi.fn(),
  runAnalysis: vi.fn(),
  refetchAnalysis: vi.fn(),
  refetchSources: vi.fn(),
  segment: null as string | null,
  progress: [] as { step: string; elapsed: number; reachedAt: number }[],
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: state.routerPush }),
  useParams: () => ({ caseId: "22222222-2222-4222-8222-222222222222" }),
  useSelectedLayoutSegment: () => state.segment,
}));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: vi.fn(),
  useIsCaseAnalysisRunning: vi.fn(),
}));
vi.mock("@/features/analysis/useRunCaseAnalysis", () => ({
  useRunCaseAnalysis: () => state.runAnalysis,
}));
vi.mock("@/features/sources/queries", () => ({ useCaseSources: vi.fn() }));
vi.mock("@/features/chat/useCaseChat", () => ({
  useIsFollowupPending: vi.fn(),
}));
vi.mock("@/features/analysis/progress", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/analysis/progress")>()),
  useAnalysisProgress: () => state.progress,
}));

function caseProjection(options: { page?: boolean; stale?: boolean } = {}): {
  result: CaseAnalysisResultRead;
  sources: CaseSourceRead[];
} {
  const source = options.page
    ? pagedDocumentSource("Page 4: received 52,000 baht.", 4)
    : narrativeSource("The reporting party named Account A.");
  const citation = options.page
    ? {
        source_id: source.id,
        exact_quote: "received 52,000 baht",
        document_id: "DOC-1",
        filename: "statement.pdf",
        page_numbers: [4],
      }
    : { source_id: source.id, exact_quote: source.exact_text };
  const summary = "The submitted material establishes a reported transaction.";
  const result = analysisResult({
    summary,
    trace_json: trace({
      summary,
      claims: [
        claim("The submitted material reports a transaction.", source.id, {
          supporting_citations: [citation],
        }),
      ],
      gaps: [
        {
          gap_id: "G-01",
          gap_key: "topic:incident-time",
          topic: "Incident time",
          status: "NOT_PROVIDED",
          description: "The incident time is missing.",
          reason: "Timing affects chronology.",
          priority: "high",
          askable: true,
        },
      ],
    }),
    external_context_json: {
      technical_augmentation: { status: "not_applicable" },
      sources_read: sourcesRead(source.id),
    },
    freshness: options.stale ? "stale" : "current",
  });
  return { result, sources: [source] };
}

interface MockOverrides {
  analysisResult?: CaseAnalysisResultRead | null;
  sources?: CaseSourceRead[];
  analysisFailed?: boolean;
  sourcesFailed?: boolean;
  followupPending?: boolean;
  analysisRunning?: boolean;
}

function configureAndRender(overrides: MockOverrides = {}) {
  const projection = caseProjection();
  const result =
    overrides.analysisResult !== undefined ? overrides.analysisResult : projection.result;
  const sourceRows = overrides.sources ?? projection.sources;

  vi.mocked(useCaseAnalysis).mockReturnValue({
    data: overrides.analysisFailed ? undefined : result,
    isLoading: false,
    isLoadingError: overrides.analysisFailed ?? false,
    refetch: state.refetchAnalysis,
  } as never);
  vi.mocked(useCaseSources).mockReturnValue({
    data: overrides.sourcesFailed ? undefined : sourceRows,
    isLoading: false,
    isLoadingError: overrides.sourcesFailed ?? false,
    refetch: state.refetchSources,
  } as never);
  vi.mocked(useIsCaseAnalysisRunning).mockReturnValue(overrides.analysisRunning ?? false);
  vi.mocked(useIsFollowupPending).mockReturnValue(overrides.followupPending ?? false);

  render(
    <AnalysisLayout>
      <p>Section content</p>
    </AnalysisLayout>,
  );
}

beforeEach(() => {
  state.routerPush.mockClear();
  state.runAnalysis.mockClear();
  state.refetchAnalysis.mockClear();
  state.refetchSources.mockClear();
  state.segment = null;
  state.progress = [];
});

describe("AnalysisLayout", () => {
  it("links every section of a finished analysis, with the counts that need reading", () => {
    configureAndRender();

    const nav = screen.getByRole("navigation", { name: "Analysis sections" });
    const links = Array.from(nav.querySelectorAll("a")).map((link) => [
      link.textContent,
      link.getAttribute("href"),
    ]);
    const base = `/case/${caseId}/analysis`;
    expect(links).toEqual([
      ["Summary", base],
      ["Findings1", `${base}/findings`],
      ["Details", `${base}/details`],
      ["Open questions1", `${base}/questions`],
      ["Report", `${base}/report`],
    ]);
    expect(screen.getByText("Section content")).toBeInTheDocument();
  });

  it("marks the summary as the section the reader is on when no section is open", () => {
    configureAndRender();

    expect(screen.getByRole("link", { name: "Summary" })).toHaveAttribute("aria-current", "page");
  });

  it("marks the open section as the one the reader is on", () => {
    state.segment = "findings";
    configureAndRender();

    const nav = screen.getByRole("navigation", { name: "Analysis sections" });
    expect(nav.querySelectorAll('[aria-current="page"]')).toHaveLength(1);
    expect(nav.querySelector('[aria-current="page"]')).toHaveTextContent("Findings");
  });

  it("offers reanalysis when the canonical result is stale", () => {
    const projection = caseProjection({ stale: true });
    configureAndRender({ analysisResult: projection.result, sources: projection.sources });
    expect(screen.getByText(/Analysis is based on older sources/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Analyze again" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Analyze latest sources/i }));
    expect(state.runAnalysis).toHaveBeenCalledOnce();
  });

  it("offers to run an up-to-date analysis again beside its status", () => {
    configureAndRender();

    fireEvent.click(screen.getByRole("button", { name: "Analyze again" }));
    expect(state.runAnalysis).toHaveBeenCalledOnce();
  });

  it("names the case's files in the analysis record", () => {
    const projection = caseProjection({ page: true });
    configureAndRender({ analysisResult: projection.result, sources: projection.sources });

    fireEvent.click(screen.getByRole("button", { name: "Analysis record" }));
    expect(screen.getByText("Documents").nextElementSibling).toHaveTextContent("statement.pdf");
  });

  it("counts the sources the analysis read, not the ones added after it", () => {
    const projection = caseProjection({ page: true });
    projection.result.external_context_json = {
      ...projection.result.external_context_json,
      followup_history: followupHistory("When was the transfer?", "At noon."),
    };
    const later = narrativeSource("Added after the analysis.", {
      id: "33333333-3333-4333-8333-333333333333",
      filename: "later.pdf",
    });
    configureAndRender({
      analysisResult: projection.result,
      sources: [...projection.sources, later],
    });

    fireEvent.click(screen.getByRole("button", { name: "Analysis record" }));
    expect(screen.getByText("Sources").nextElementSibling).toHaveTextContent("2 · 1 cited");
    expect(screen.getByText("Documents").nextElementSibling).toHaveTextContent(/^statement\.pdf$/);
  });

  it("says the analysis is being updated while a run is in flight", () => {
    configureAndRender({ analysisRunning: true });

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
    configureAndRender({ analysisResult: null });

    expect(screen.getByRole("heading", { name: "Not analyzed yet" })).toBeInTheDocument();
    expect(screen.queryByText("Section content")).not.toBeInTheDocument();
    expect(screen.queryByRole("navigation", { name: "Analysis sections" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    expect(state.runAnalysis).toHaveBeenCalledOnce();
  });

  it("waits for a follow-up answer before a first analysis, and offers no second one", () => {
    configureAndRender({ analysisResult: null, followupPending: true });

    expect(screen.getByRole("heading", { name: "Analyzing…" })).toBeInTheDocument();
    expect(screen.getByText(/with your answer/)).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Not analyzed yet" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Analyze" })).not.toBeInTheDocument();
  });

  it("names the step a first analysis is on while it runs", () => {
    const now = Date.now();
    state.progress = [
      { step: "assess", elapsed: 0, reachedAt: now - 30_000 },
      { step: "read", elapsed: 12, reachedAt: now - 18_000 },
    ];
    configureAndRender({ analysisResult: null, analysisRunning: true });

    const list = screen.getByRole("list", { name: "Analysis progress" });
    expect(list.querySelector('[aria-current="step"]')).toHaveTextContent(
      "Reading the sources: claims and quotations",
    );
  });

  it("names the step while an analysis that is already shown is updated", () => {
    state.progress = [{ step: "judge", elapsed: 80, reachedAt: Date.now() }];
    configureAndRender({ analysisRunning: true });

    expect(
      screen
        .getByRole("list", { name: "Analysis progress" })
        .querySelector('[aria-current="step"]'),
    ).toHaveTextContent("Judging: summary, open questions, ATT&CK");
  });

  it("offers to load a failed analysis again, never to run a new one", () => {
    configureAndRender({ analysisFailed: true });

    expect(
      screen.getByRole("heading", { name: "Analysis could not be loaded" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Not analyzed yet" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Analyze/ })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(state.refetchAnalysis).toHaveBeenCalledOnce();
    expect(state.runAnalysis).not.toHaveBeenCalled();
  });

  it("does not show findings stripped of their sources when the sources fail to load", () => {
    configureAndRender({ sourcesFailed: true });

    expect(
      screen.getByRole("heading", { name: "Analysis could not be loaded" }),
    ).toBeInTheDocument();
    expect(screen.queryByText("Section content")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(state.refetchSources).toHaveBeenCalledOnce();
    expect(state.refetchAnalysis).not.toHaveBeenCalled();
  });
});
