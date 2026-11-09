import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnalysisSummary } from "@/features/analysis/AnalysisSummary";
import type { CaseAnalysisClaim } from "@/lib/api/types";
import {
  analysisResult,
  caseId,
  claim,
  narrativeSource,
  sourcesRead,
  trace,
} from "@/test/fixtures";

const source = narrativeSource("Two rooms were broken into at the dormitory.");
const summary = "Room 402 was entered with a hidden key [A-01]. Room 503 was forced open [A-02].";
const flaggedNote =
  "A finding behind this sentence was not clearly supported by its cited Source. Check it before relying on the sentence.";

function claims(first: "supported" | "not_supported", second: "supported" | "not_supported") {
  const withVerdict = (
    verdict: "supported" | "not_supported",
  ): Pick<CaseAnalysisClaim, "semantic_grounding"> => ({
    semantic_grounding: {
      verdict,
      reason: verdict === "supported" ? "lr_supported" : "lr_not_supported",
    },
  });
  return [
    claim("Room 402 was entered with a hidden key.", source.id, withVerdict(first)),
    claim("Room 503 was forced open with a screwdriver.", source.id, {
      claim_id: "A-02",
      ...withVerdict(second),
    }),
  ];
}

function analysisWith(
  first: "supported" | "not_supported",
  second: "supported" | "not_supported",
  firstSupport: "bound" | "mixed" = "bound",
) {
  return analysisResult({
    summary,
    trace_json: trace({
      summary,
      summary_units: [
        {
          text: "Room 402 was entered with a hidden key",
          claim_ids: ["A-01"],
          support: firstSupport,
        },
        { text: "Room 503 was forced open", claim_ids: ["A-02"], support: "bound" },
      ],
      claims: claims(first, second),
    }),
    external_context_json: {
      technical_augmentation: { status: "not_applicable" },
      sources_read: sourcesRead(source.id),
    },
  });
}

let analysis = analysisWith("supported", "supported");

vi.mock("next/navigation", () => ({ useParams: () => ({ caseId }) }));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => ({ data: analysis, isLoading: false }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () => ({ data: [source], isLoading: false }),
}));

function summarySection() {
  return screen.getByRole("heading", { name: "What happened" }).closest("section") as HTMLElement;
}

describe("AnalysisSummary with a finding the source check flagged", () => {
  it("gives the sentence resting on it a raised letter and a plain note under the paragraph", () => {
    analysis = analysisWith("supported", "not_supported");
    render(<AnalysisSummary />);

    const section = summarySection();
    expect(within(section).getAllByRole("paragraph")[0]).toHaveTextContent(
      "Room 402 was entered with a hidden key1. Room 503 was forced open2a.",
    );
    expect(within(section).getAllByText(flaggedNote)).toHaveLength(1);
    expect(within(section).getByText(flaggedNote)).toHaveTextContent(`a ${flaggedNote}`);
  });

  it("shows nothing new when no finding behind a sentence was flagged", () => {
    analysis = analysisWith("supported", "supported");
    render(<AnalysisSummary />);

    const section = summarySection();
    expect(within(section).getAllByRole("paragraph")[0]).toHaveTextContent(
      "Room 402 was entered with a hidden key1. Room 503 was forced open2.",
    );
    expect(within(section).queryByText(/not clearly supported/)).not.toBeInTheDocument();
    expect(within(section).queryByText("a", { selector: "sup" })).not.toBeInTheDocument();
  });

  it("joins both reasons under one letter when a sentence has both", () => {
    analysis = analysisWith("not_supported", "supported", "mixed");
    render(<AnalysisSummary />);

    const section = summarySection();
    expect(within(section).getAllByRole("paragraph")[0]).toHaveTextContent(
      "Room 402 was entered with a hidden key1a. Room 503 was forced open2.",
    );
    expect(
      within(section).getByText(
        `Only some linked claims have resolved source citations. ${flaggedNote}`,
        { exact: false },
      ),
    ).toBeInTheDocument();
  });
});
