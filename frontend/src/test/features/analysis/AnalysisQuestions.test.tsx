import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnalysisQuestions } from "@/features/analysis/AnalysisQuestions";
import type { CaseAnalysisGap } from "@/lib/api/types";
import { analysisResult, caseId, narrativeSource, sourcesRead, trace } from "@/test/fixtures";

const source = narrativeSource("Room 503 was broken into.");
const state = vi.hoisted(() => ({ gaps: [] as CaseAnalysisGap[] }));

function gap(overrides: Partial<CaseAnalysisGap>): CaseAnalysisGap {
  return {
    gap_id: "G-01",
    gap_key: "how_much",
    topic: "how_much",
    status: "NOT_PROVIDED",
    description: "The total value taken from room 503 is unknown.",
    reason: "The value decides the charge.",
    priority: "medium",
    askable: true,
    ...overrides,
  };
}

vi.mock("next/navigation", () => ({ useParams: () => ({ caseId }) }));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => ({
    data: analysisResult({
      trace_json: trace({ summary: "A theft.", gaps: state.gaps }),
      external_context_json: { sources_read: sourcesRead(source.id) },
    }),
    isLoading: false,
  }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () => ({ data: [source], isLoading: false }),
}));

describe("AnalysisQuestions", () => {
  it("names a checklist gap in words, not by its key", () => {
    state.gaps = [gap({})];
    render(<AnalysisQuestions />);

    expect(screen.getByRole("heading", { name: "How much" })).toBeInTheDocument();
    expect(screen.queryByText("how_much")).not.toBeInTheDocument();
    expect(screen.getByText("The total value taken from room 503 is unknown.")).toBeInTheDocument();
    expect(screen.getByText("Needs an answer")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Why it matters/ }));
    expect(screen.getByText("The value decides the charge.")).toBeInTheDocument();
  });

  it("keeps a topic the analysis wrote in words", () => {
    state.gaps = [gap({ gap_key: "log_file", topic: "Whether a log file exists" })];
    render(<AnalysisQuestions />);

    expect(screen.getByRole("heading", { name: "Whether a log file exists" })).toBeInTheDocument();
  });

  it("says nothing is missing when the analysis left no questions", () => {
    state.gaps = [];
    render(<AnalysisQuestions />);

    expect(screen.getByText("Nothing is missing from this analysis.")).toBeInTheDocument();
  });
});
