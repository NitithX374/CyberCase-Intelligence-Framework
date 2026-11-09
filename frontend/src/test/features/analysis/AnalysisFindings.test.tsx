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
        },
        supporting_citations: [
          {
            source_id: source.id,
            exact_quote: "received 52,000 baht",
            pointer_state: "recovered",
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
  it("keeps each finding's number from the whole list under every filter", () => {
    render(<AnalysisFindings />);

    const numbered = () =>
      screen
        .getAllByRole("article")
        .map((article) => [article.getAttribute("aria-label"), article.textContent]);
    const numberOf = (text: string) =>
      numbered().find(([, content]) => content?.includes(text))?.[0];

    expect(numbered()).toHaveLength(1);
    expect(numberOf("Another transaction was mentioned.")).toBe("Finding 3");

    fireEvent.click(screen.getByRole("button", { name: "All 4" }));
    expect(numberOf("The statement reports a transfer.")).toBe("Finding 1");
    expect(numberOf("The transfer went to Account B.")).toBe("Finding 2");
    expect(numberOf("Another transaction was mentioned.")).toBe("Finding 3");
    expect(numberOf("A legacy report has a Source link.")).toBe("Finding 4");

    fireEvent.click(screen.getByRole("button", { name: /Not confirmed/ }));
    expect(numbered()).toHaveLength(1);
    expect(numberOf("The transfer went to Account B.")).toBe("Finding 2");
  });

  it("opens on All when nothing is flagged, with an accurate empty To check filter", () => {
    navigation.result = structuredClone(analysis);
    navigation.result.trace_json!.claims[2].semantic_grounding = null;
    render(<AnalysisFindings />);
    expect(screen.getByRole("button", { name: "All 4" })).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(screen.getByRole("button", { name: "To check 0" }));
    expect(screen.getByText("No findings to check in this analysis.")).toBeVisible();
    expect(screen.queryByRole("article")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "All 4" }));
    expect(screen.getByText("The statement reports a transfer.", { selector: "p" })).toBeVisible();
  });

  it("opens on To check, listing only the findings the verifier warned about, and All keeps the rest", () => {
    render(<AnalysisFindings />);
    expect(screen.getByRole("button", { name: "To check 1" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByText("Another transaction was mentioned.", { selector: "p" })).toBeVisible();
    expect(screen.getByText(/did not clearly support this finding/)).toBeVisible();
    expect(screen.queryByText("The statement reports a transfer.")).not.toBeInTheDocument();
    expect(screen.queryByText("The transfer went to Account B.")).not.toBeInTheDocument();
    expect(screen.queryByText("A legacy report has a Source link.")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "All 4" }));
    expect(screen.getByText("The statement reports a transfer.", { selector: "p" })).toBeVisible();
    expect(screen.getByText("A legacy report has a Source link.", { selector: "p" })).toBeVisible();
  });

  it("offers no Supported filter", () => {
    render(<AnalysisFindings />);
    expect(screen.queryByRole("button", { name: /Supported/ })).not.toBeInTheDocument();
    expect(
      screen.getAllByRole("button", { name: /^(All|To check|Not confirmed) \d/ }),
    ).toHaveLength(3);
  });

  it("opens already narrowed to the flagged findings when the link asked for them", () => {
    navigation.search = "status=flagged";
    render(<AnalysisFindings />);

    expect(screen.getByRole("button", { name: "To check 1" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getAllByRole("article")).toHaveLength(1);
    expect(screen.getByText("Another transaction was mentioned.", { selector: "p" })).toBeVisible();
  });

  it("opens on All for an old link that asked for the supported findings", () => {
    navigation.search = "status=supported";
    render(<AnalysisFindings />);

    expect(screen.getByRole("button", { name: "All 4" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getAllByRole("article")).toHaveLength(4);
  });

  it("lists every finding and opens the exact page a quotation came from", () => {
    render(<AnalysisFindings />);
    fireEvent.click(screen.getByRole("button", { name: "All 4" }));

    expect(
      screen.getByText("The statement reports a transfer.", { selector: "p" }),
    ).toBeInTheDocument();
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
    expect(
      screen.getByText("The statement reports a transfer.", { selector: "p" }),
    ).toBeInTheDocument();
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
    expect(
      screen.getByText("The statement reports a transfer.", { selector: "p" }),
    ).toBeInTheDocument();
  });
});
