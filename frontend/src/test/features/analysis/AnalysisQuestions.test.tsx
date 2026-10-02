import { fireEvent, render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AnalysisQuestions } from "@/features/analysis/AnalysisQuestions";
import type { CaseAnalysisClaim, CaseAnalysisGap } from "@/lib/api/types";
import {
  analysisResult,
  caseId,
  claim,
  narrativeSource,
  sourcesRead,
  trace,
} from "@/test/fixtures";

const source = narrativeSource("Room 503 was broken into.");
const state = vi.hoisted(() => ({
  gaps: [] as CaseAnalysisGap[],
  claims: [] as CaseAnalysisClaim[],
}));

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
      trace_json: trace({ summary: "A theft.", gaps: state.gaps, claims: state.claims }),
      external_context_json: { sources_read: sourcesRead(source.id) },
    }),
    isLoading: false,
  }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () => ({ data: [source], isLoading: false }),
}));

describe("AnalysisQuestions", () => {
  beforeEach(() => {
    state.claims = [];
  });

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

  it("lists the findings a gap affects behind a toggle that counts them", () => {
    state.claims = [
      claim("Room 503 was broken into.", source.id),
      claim("The safe in room 503 was empty.", source.id, { claim_id: "A-02" }),
    ];
    state.gaps = [gap({ affected_claim_ids: ["A-02", "A-01"] })];
    render(<AnalysisQuestions />);

    const toggle = screen.getByRole("button", { name: /^Affected findings \(2\)/ });
    expect(toggle).toHaveAttribute("aria-expanded", "false");
    expect(screen.queryByRole("list", { name: "Affected findings" })).not.toBeInTheDocument();

    fireEvent.click(toggle);

    expect(toggle).toHaveAttribute("aria-expanded", "true");
    const listed = within(screen.getByRole("list", { name: "Affected findings" }));
    expect(listed.getAllByRole("listitem").map((item) => item.textContent)).toEqual([
      "The safe in room 503 was empty.",
      "Room 503 was broken into.",
    ]);
  });

  it("offers no affected findings when the gap names none the analysis holds", () => {
    state.claims = [claim("Room 503 was broken into.", source.id)];
    state.gaps = [
      gap({ affected_claim_ids: [] }),
      gap({ gap_id: "G-02", gap_key: "when", topic: "when", affected_claim_ids: ["A-09"] }),
    ];
    render(<AnalysisQuestions />);

    expect(screen.getAllByRole("button", { name: /Why it matters/ })).toHaveLength(2);
    expect(screen.queryByRole("button", { name: /Affected findings/ })).not.toBeInTheDocument();
  });
});
