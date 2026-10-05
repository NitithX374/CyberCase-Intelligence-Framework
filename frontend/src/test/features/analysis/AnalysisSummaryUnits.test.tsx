import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AnalysisSummary } from "@/features/analysis/AnalysisSummary";
import { useCaseReports } from "@/features/reports/queries";
import {
  analysisResult,
  caseId,
  claim,
  narrativeSource,
  sourcesRead,
  trace,
} from "@/test/fixtures";

const source = narrativeSource("Two rooms were broken into at the dormitory.");
const summary =
  "Room 402 was entered with a hidden key [A-01]. Room 503 was forced open [A-02]. The tenant is to blame.";

const analysis = analysisResult({
  summary,
  trace_json: trace({
    summary,
    summary_units: [
      { text: "Room 402 was entered with a hidden key", claim_ids: ["A-01"], support: "bound" },
      { text: "Room 503 was forced open", claim_ids: ["A-02"], support: "unbound" },
      { text: "The tenant is to blame.", claim_ids: [], support: "no_claim" },
    ],
    claims: [
      claim("Room 402 was entered with a hidden key.", source.id),
      claim("Room 503 was forced open with a screwdriver.", source.id, {
        claim_id: "A-02",
        epistemic_status: "not_confirmed",
        supporting_citations: [],
      }),
    ],
  }),
  external_context_json: {
    technical_augmentation: { status: "not_applicable" },
    sources_read: sourcesRead(source.id),
  },
});

vi.mock("next/navigation", () => ({ useParams: () => ({ caseId }) }));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => ({ data: analysis, isLoading: false }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () => ({ data: [source], isLoading: false }),
}));
vi.mock("@/features/reports/queries", () => ({ useCaseReports: vi.fn() }));

beforeEach(() => {
  vi.mocked(useCaseReports).mockReturnValue({ data: [] } as never);
});

describe("AnalysisSummary with a summary that names its claims", () => {
  it("reads the summary as one paragraph and links each raised number to its finding", () => {
    render(<AnalysisSummary />);

    const section = screen
      .getByRole("heading", { name: "Summary" })
      .closest("section") as HTMLElement;
    const links = within(section).getAllByRole("link");
    expect(
      links.map((link) => [
        link.textContent,
        link.getAttribute("aria-label"),
        link.getAttribute("href"),
      ]),
    ).toEqual([
      ["1", "Finding 1", `/case/${caseId}/analysis/findings?finding=A-01`],
      ["2", "Finding 2", `/case/${caseId}/analysis/findings?finding=A-02`],
    ]);
    const paragraph = within(section).getAllByRole("paragraph")[0];
    expect(paragraph).toHaveTextContent(
      "Room 402 was entered with a hidden key1. Room 503 was forced open2a. The tenant is to blame.b",
    );
    expect(within(section).getAllByRole("paragraph")).toHaveLength(1);
  });

  it("says under the paragraph what no checked quotation supports, by letter", () => {
    render(<AnalysisSummary />);

    expect(screen.getAllByText("No cited quotation was found in the sources.")).toHaveLength(1);
    expect(screen.getAllByText("Not linked to any claim.")).toHaveLength(1);
    expect(screen.queryByText(/Some cited quotations/)).not.toBeInTheDocument();
  });

  it("does not print the brackets as plain text", () => {
    render(<AnalysisSummary />);

    expect(screen.queryByText(/\[A-0\d\]/)).not.toBeInTheDocument();
  });
});
