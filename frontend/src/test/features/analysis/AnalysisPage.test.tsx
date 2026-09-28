import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  analysisResult,
  association,
  caseId,
  claim,
  followupHistory,
  narrativeSource,
  trace,
} from "@/test/fixtures";
import { AnalysisPage } from "@/features/analysis/AnalysisPage";

const answer = "The attacker came in through the web server.";

const analysis = analysisResult({
  summary: answer,
  trace_json: trace({
    summary: answer,
    claims: [claim(answer, "QA-01")],
    mitre_associations: [
      association("T1190", {
        reason: "The answer describes entry through a public web server.",
        plain_meaning: "The attacker used a flaw in a public-facing application.",
      }),
    ],
    retrieval_context_id: "retrieval-1",
  }),
  retrieval_context_id: "retrieval-1",
  external_context_json: {
    followup_history: followupHistory("How did the attacker get in?", answer),
    technical_augmentation: {
      version: "case_mitre_augmentation_v1",
      status: "retrieved_with_matches",
      retrieval_context_id: "retrieval-1",
      mitre_table: [
        {
          technique_id: "T1190",
          name: "Exploit Public-Facing Application",
          tactic: "Initial Access",
          description: "Adversaries may exploit a public-facing application.",
        },
      ],
      association_ids: ["MA-01"],
    },
  },
});

const sourcesState = vi.hoisted(() => ({ failed: false }));

vi.mock("next/navigation", () => ({ useParams: () => ({ caseId }) }));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => ({ data: analysis, isLoading: false }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () =>
    sourcesState.failed
      ? { data: undefined, isLoading: false, isLoadingError: true }
      : { data: [narrativeSource("Payroll files were encrypted overnight.")], isLoading: false },
}));
vi.mock("@/features/chat/useCaseChat", () => ({
  useCaseChatQuery: () => {
    throw new Error("The analysis page does not read the live chat.");
  },
}));
vi.mock("@/features/analysis/CaseOverviewView", () => ({ CaseOverviewView: () => null }));
vi.mock("@/features/reports/CaseReportView", () => ({ CaseReportView: () => null }));

beforeEach(() => {
  sourcesState.failed = false;
});

describe("AnalysisPage", () => {
  it("shows ATT&CK context that rests on the follow-up answer the analysis recorded", () => {
    render(<AnalysisPage />);

    expect(
      screen.getByRole("heading", { name: "Exploit Public-Facing Application" }),
    ).toBeInTheDocument();
    expect(screen.getByText(`“${answer}”`)).toBeInTheDocument();
    expect(screen.getByText("Follow-up answer QA-01")).toBeInTheDocument();
  });

  it("withholds ATT&CK context while the case sources cannot be loaded", () => {
    sourcesState.failed = true;
    render(<AnalysisPage />);

    expect(
      screen.queryByRole("heading", { name: "Exploit Public-Facing Application" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText("No ATT&CK context is available for this analysis."),
    ).toBeInTheDocument();
  });
});
