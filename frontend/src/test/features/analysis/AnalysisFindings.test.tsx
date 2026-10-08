import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AnalysisFindings } from "@/features/analysis/AnalysisFindings";
import type { CaseAnalysisResultRead } from "@/lib/api/types";
import {
  analysisResult,
  caseId,
  claim,
  pagedDocumentSource,
  sourcesRead,
  trace,
} from "@/test/fixtures";

const source = pagedDocumentSource("Page 4: received 52,000 baht.", 4);

const analysis = analysisResult({
  trace_json: trace({
    summary: "A transfer was reported.",
    claims: [
      claim("The statement reports a transfer.", source.id, {
        semantic_grounding: {
          verdict: "supported",
          reason: "lr_supported",
          threshold: 0.5,
          selection_ms: 0,
          duration_ms: 0,
        },
        supporting_citations: [
          {
            source_id: source.id,
            exact_quote: "received 52,000 baht",
            document_id: "DOC-1",
            filename: "statement.pdf",
            page_numbers: [4],
          },
        ],
      }),
      claim("The transfer went to Account B.", source.id, {
        claim_id: "A-02",
        epistemic_status: "not_confirmed",
        supporting_citations: [],
      }),
      claim("Another transaction was mentioned.", source.id, {
        claim_id: "A-03",
        semantic_grounding: {
          verdict: "not_supported",
          reason: "lr_not_supported",
          threshold: 0.5,
          selection_ms: 0,
          duration_ms: 0,
        },
      }),
      claim("A legacy report has a Source link.", source.id, { claim_id: "A-04" }),
    ],
  }),
  external_context_json: { sources_read: sourcesRead(source.id) },
});

const navigation = vi.hoisted(() => ({
  search: "",
  result: undefined as CaseAnalysisResultRead | undefined,
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ caseId }),
  useSearchParams: () => new URLSearchParams(navigation.search),
}));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => ({ data: navigation.result, isLoading: false }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () => ({ data: [source], isLoading: false }),
}));

beforeEach(() => {
  navigation.search = "";
  navigation.result = analysis;
});

describe("AnalysisFindings", () => {
  it("shows an accurate empty Supported filter and lets the reader return to All", () => {
    navigation.result = structuredClone(analysis);
    navigation.result.trace_json!.claims[0].semantic_grounding = null;
    render(<AnalysisFindings />);
    fireEvent.click(screen.getByRole("button", { name: "Supported 0" }));
    expect(screen.getByText("No supported findings in this analysis.")).toBeVisible();
    expect(screen.queryByRole("article")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "All 4" }));
    expect(screen.getByText("The statement reports a transfer.")).toBeVisible();
  });

  it("filters by saved Source support and retains the other findings under All", () => {
    render(<AnalysisFindings />);
    fireEvent.click(screen.getByRole("button", { name: "Supported 1" }));
    expect(screen.getByRole("button", { name: "Supported 1" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByText("The statement reports a transfer.")).toBeVisible();
    expect(screen.queryByText("The transfer went to Account B.")).not.toBeInTheDocument();
    expect(screen.queryByText("Another transaction was mentioned.")).not.toBeInTheDocument();
    expect(screen.queryByText("A legacy report has a Source link.")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "statement.pdf · p. 4" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("received 52,000 baht");
    fireEvent.click(screen.getByRole("button", { name: "Close source" }));
    fireEvent.click(screen.getByRole("button", { name: "All 4" }));
    expect(screen.getByText("Another transaction was mentioned.")).toBeVisible();
    expect(screen.getByText("A legacy report has a Source link.")).toBeVisible();
  });

  it("lists every finding and opens the exact page a quotation came from", () => {
    render(<AnalysisFindings />);

    expect(screen.getByText("The statement reports a transfer.")).toBeInTheDocument();
    expect(screen.getByText("The transfer went to Account B.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "statement.pdf · p. 4" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("received 52,000 baht");
  });

  it("narrows to findings marked not confirmed and separates Source linkage from semantic support", () => {
    render(<AnalysisFindings />);

    fireEvent.click(screen.getByRole("button", { name: /Not confirmed/ }));

    expect(screen.getByRole("button", { name: /Not confirmed/ })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.queryByText("The statement reports a transfer.")).not.toBeInTheDocument();
    expect(screen.getByText("The transfer went to Account B.")).toBeInTheDocument();
    expect(screen.getByText(/semantic support is shown separately/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /All/ }));
    expect(screen.getByText("The statement reports a transfer.")).toBeInTheDocument();
  });

  it("opens already narrowed when the link asked for the findings not confirmed", () => {
    navigation.search = "status=not_confirmed";
    render(<AnalysisFindings />);

    expect(screen.queryByText("The statement reports a transfer.")).not.toBeInTheDocument();
    expect(screen.getByText("The transfer went to Account B.")).toBeInTheDocument();
  });

  it("scrolls to the finding a summary link named", async () => {
    const scrollIntoView = vi.fn();
    Element.prototype.scrollIntoView = scrollIntoView;
    navigation.search = "finding=A-02";

    const { container } = render(<AnalysisFindings />);

    await waitFor(() => expect(scrollIntoView).toHaveBeenCalledTimes(1));
    expect(scrollIntoView.mock.contexts[0]).toBe(container.querySelector("#finding-A-02"));
    expect(screen.getByText("The statement reports a transfer.")).toBeInTheDocument();
  });
});
