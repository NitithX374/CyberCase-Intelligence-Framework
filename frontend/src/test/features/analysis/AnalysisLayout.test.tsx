import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi, beforeEach } from "vitest";
import { AnalysisLayout } from "@/features/analysis/AnalysisLayout";
import type { CaseAnalysisResultRead, CaseSourceCitation, CaseSourceRead } from "@/lib/api/types";
import { useAnalysisAvailability, useCaseAnalysis } from "@/features/analysis/queries";
import { useCaseSources } from "@/features/sources/queries";
import { useIsFollowupPending } from "@/features/chat/useCaseChat";
import {
  analysisResult,
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
  useAnalysisAvailability: vi.fn(),
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
  const citation: CaseSourceCitation = options.page
    ? {
        source_id: source.id,
        exact_quote: "received 52,000 baht",
        pointer_state: "recovered",
        document_id: "DOC-1",
        filename: "statement.pdf",
        page_numbers: [4],
      }
    : { source_id: source.id, exact_quote: source.exact_text, pointer_state: "recovered" };
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
  waitingForFollowup?: boolean;
}

function configureAndRender(
  overrides: MockOverrides = {},
  children: ReactNode = <p>Section content</p>,
) {
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
  const isUpdating = Boolean(overrides.analysisRunning || overrides.followupPending);
  vi.mocked(useAnalysisAvailability).mockReturnValue({
    isUpdating,
    isWaitingForFollowup: overrides.waitingForFollowup ?? false,
    canAnalyze: !isUpdating && !overrides.waitingForFollowup,
  });
  vi.mocked(useIsFollowupPending).mockReturnValue(overrides.followupPending ?? false);

  render(<AnalysisLayout>{children}</AnalysisLayout>);
}

function statValue(label: string) {
  return screen.getByText(label, { selector: "p" }).previousElementSibling?.textContent;
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
  it("disables the first Analyze button while a question awaits an answer", () => {
    configureAndRender({ analysisResult: null, waitingForFollowup: true });
    expect(screen.getByRole("heading", { name: "Waiting for your answer" })).toBeVisible();
    expect(screen.getByText(/Analysis continues automatically/)).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    expect(screen.getByRole("button", { name: "Analyze" })).toBeDisabled();
    expect(state.runAnalysis).not.toHaveBeenCalled();
  });

  it("asks for the follow-up answer on an older analysis, and offers no Analyze of its own", () => {
    const projection = caseProjection({ stale: true });
    configureAndRender({ analysisResult: projection.result, waitingForFollowup: true });
    expect(screen.getByRole("status")).toHaveTextContent("Answer the follow-up question in Ask.");
    expect(screen.queryByRole("button", { name: /Analyze/ })).not.toBeInTheDocument();
  });

  it("withholds Analyze again while a saved analysis awaits an answer", () => {
    configureAndRender({ waitingForFollowup: true });
    expect(screen.queryByRole("button", { name: "Analyze again" })).not.toBeInTheDocument();
  });

  it("counts what the overview holds, with the case cards beside the page", () => {
    configureAndRender();

    expect(statValue("findings")).toBe("1");
    expect(statValue("to check")).toBe("0");
    expect(statValue("open questions")).toBe("1");
    expect(statValue("source read")).toBe("1");
    expect(screen.queryByText("sources read")).not.toBeInTheDocument();
    expect(screen.getByText("Section content")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "What happened" })).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Open questions" }).closest("section"),
    ).toHaveAttribute("id", "section-attention");
    expect(screen.getByRole("heading", { name: "Last analysis" })).toBeInTheDocument();
  });

  it("gives a fact page the full width, without the overview cards", () => {
    state.segment = "people";
    configureAndRender();

    expect(screen.getByText("Section content")).toBeInTheDocument();
    expect(statValue("findings")).toBe("1");
    expect(screen.queryByRole("heading", { name: "What happened" })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Open questions" })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Last analysis" })).not.toBeInTheDocument();
  });

  it("counts flagged findings as to check", () => {
    const projection = caseProjection();
    const claims = projection.result.trace_json!.claims;
    projection.result.trace_json!.claims = [
      {
        ...claims[0],
        semantic_grounding: { verdict: "not_supported", reason: "lr_not_supported" },
      },
    ];
    configureAndRender({ analysisResult: projection.result, sources: projection.sources });

    expect(statValue("to check")).toBe("1");
    expect(statValue("open questions")).toBe("1");
  });

  it("opens a folded section the link's hash names", () => {
    window.location.hash = "#section-references";
    configureAndRender(
      {},
      <details id="section-references">
        <summary>Outside references</summary>
        <p>ATT&amp;CK and Thai law</p>
      </details>,
    );

    const folded = document.getElementById("section-references") as HTMLDetailsElement;
    expect(folded.open).toBe(true);
    window.location.hash = "";
  });

  it("says when the analysis is behind the sources, and leaves Analyze to the top bar", () => {
    const projection = caseProjection({ stale: true });
    configureAndRender({ analysisResult: projection.result, sources: projection.sources });

    expect(screen.getByText("Out of date")).toBeInTheDocument();
    expect(screen.queryByText(/Analysis is based on older sources/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Analyze/ })).not.toBeInTheDocument();
  });

  it("says an up-to-date analysis is current and when it was made", () => {
    configureAndRender();

    expect(screen.getByText("Up to date")).toBeInTheDocument();
    expect(screen.getByText(/^Analyzed/)).toContainElement(
      document.querySelector('time[datetime="2026-09-10T00:00:00Z"]') as HTMLElement,
    );
    expect(screen.queryByRole("button", { name: /Analyze/ })).not.toBeInTheDocument();
  });

  it("keeps the analysis record folded until it is asked for", () => {
    configureAndRender();

    const toggle = screen.getByRole("button", { name: "Analysis record" });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByText("Source revision")).not.toBeInTheDocument();
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByText("Source revision").nextElementSibling).toHaveTextContent("1");
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
    expect(screen.queryByRole("button", { name: /Analyze/ })).not.toBeInTheDocument();
  });

  it("offers to analyze a case that has sources but no analysis yet", () => {
    configureAndRender({ analysisResult: null });

    expect(screen.getByRole("heading", { name: "Not analyzed yet" })).toBeInTheDocument();
    expect(screen.queryByText("Section content")).not.toBeInTheDocument();
    expect(screen.queryByRole("navigation", { name: "On this page" })).not.toBeInTheDocument();
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
    expect(list.querySelector('[aria-current="step"]')).toHaveTextContent("Reading case sources");
  });

  it("names the step while an analysis that is already shown is updated", () => {
    state.progress = [{ step: "judge", elapsed: 80, reachedAt: Date.now() }];
    configureAndRender({ analysisRunning: true });

    expect(
      screen
        .getByRole("list", { name: "Analysis progress" })
        .querySelector('[aria-current="step"]'),
    ).toHaveTextContent("Preparing the summary and case details");
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

  describe("scrolling", () => {
    let scrolled: Element[];

    beforeEach(() => {
      scrolled = [];
      Object.defineProperty(Element.prototype, "scrollIntoView", {
        configurable: true,
        value(this: Element) {
          scrolled.push(this);
        },
      });
    });

    afterEach(() => {
      delete (Element.prototype as Partial<Element>).scrollIntoView;
      window.location.hash = "";
    });

    it("leaves the page where it is when the section has nothing to scroll to", () => {
      state.segment = "details";
      configureAndRender();

      expect(scrolled).toEqual([]);
    });

    it("opens and brings into view the outside references for the old details route", () => {
      state.segment = "details";
      configureAndRender(
        {},
        <details id="section-references">
          <summary>Outside references</summary>
        </details>,
      );

      const folded = document.getElementById("section-references") as HTMLDetailsElement;
      expect(folded.open).toBe(true);
      expect(scrolled).toEqual([folded]);
    });

    it("brings the open questions card into view for the questions route", () => {
      state.segment = "questions";
      configureAndRender();

      expect(scrolled).toEqual([
        screen.getByRole("heading", { name: "Open questions" }).closest("section"),
      ]);
    });

    it("brings a linked ATT&CK entry into view instead of the top of the section", () => {
      window.location.hash = "#mitre-T1566";
      state.segment = "details";
      configureAndRender({}, <article id="mitre-T1566">T1566 Phishing</article>);

      expect(scrolled).toEqual([screen.getByRole("article")]);
    });
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
