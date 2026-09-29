import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AnalysisFindings } from "@/features/analysis/AnalysisFindings";
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
    ],
  }),
  external_context_json: { sources_read: sourcesRead(source.id) },
});

const navigation = vi.hoisted(() => ({ search: "" }));

vi.mock("next/navigation", () => ({
  useParams: () => ({ caseId }),
  useSearchParams: () => new URLSearchParams(navigation.search),
}));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => ({ data: analysis, isLoading: false }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () => ({ data: [source], isLoading: false }),
}));

beforeEach(() => {
  navigation.search = "";
});

describe("AnalysisFindings", () => {
  it("lists every finding and opens the exact page a quotation came from", () => {
    render(<AnalysisFindings />);

    expect(screen.getByText("The statement reports a transfer.")).toBeInTheDocument();
    expect(screen.getByText("The transfer went to Account B.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "statement.pdf · p. 4" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("received 52,000 baht");
  });

  it("narrows to the findings whose quotation was not found, and says what that means", () => {
    render(<AnalysisFindings />);

    fireEvent.click(screen.getByRole("button", { name: /Not confirmed/ }));

    expect(screen.getByRole("button", { name: /Not confirmed/ })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.queryByText("The statement reports a transfer.")).not.toBeInTheDocument();
    expect(screen.getByText("The transfer went to Account B.")).toBeInTheDocument();
    expect(screen.getByText(/not found there word for word/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /All/ }));
    expect(screen.getByText("The statement reports a transfer.")).toBeInTheDocument();
  });

  it("opens already narrowed when the link asked for the findings not confirmed", () => {
    navigation.search = "status=not_confirmed";
    render(<AnalysisFindings />);

    expect(screen.queryByText("The statement reports a transfer.")).not.toBeInTheDocument();
    expect(screen.getByText("The transfer went to Account B.")).toBeInTheDocument();
  });
});
