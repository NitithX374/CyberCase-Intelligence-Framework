import { render, screen, within } from "@testing-library/react";
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
import { AnalysisDetails } from "@/features/analysis/AnalysisDetails";

const answer = "The attacker came in through the web server.";

const analysis = analysisResult({
  summary: answer,
  trace_json: trace({
    summary: answer,
    claims: [claim(answer, "QA-01")],
    timeline: [
      { time: "Monday night", event: "The web server was breached.", claim_ids: ["A-01"] },
    ],
    involved_parties: [{ name: "Acme Ltd", role: "Victim", claim_ids: ["A-01"] }],
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

const sourcesState = vi.hoisted(() => ({ failed: false, claimsOnly: false }));

vi.mock("next/navigation", () => ({ useParams: () => ({ caseId }) }));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => ({
    data: sourcesState.claimsOnly
      ? {
          ...analysis,
          trace_json: { ...analysis.trace_json, involved_parties: [], timeline: [], impacts: [] },
        }
      : analysis,
    isLoading: false,
  }),
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

beforeEach(() => {
  sourcesState.failed = false;
  sourcesState.claimsOnly = false;
});

describe("AnalysisDetails", () => {
  it("links claims-only details to Findings without inventing separate structures", () => {
    sourcesState.claimsOnly = true;
    render(<AnalysisDetails />);
    expect(
      screen.getByText("People, dates, events and impacts are recorded in the claims."),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open Findings and their sources" })).toHaveAttribute(
      "href",
      `/case/${caseId}/analysis/findings`,
    );
    expect(screen.queryByRole("heading", { name: /Timeline/ })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "MITRE ATT&CK" })).toBeInTheDocument();
  });
  it("lists the timeline and parties, then the ATT&CK context below them", () => {
    render(<AnalysisDetails />);

    const timeline = screen.getByRole("heading", { name: /Timeline/ });
    const attack = screen.getByRole("heading", { name: "MITRE ATT&CK" });
    expect(screen.getByText("The web server was breached.")).toBeInTheDocument();
    expect(screen.getByText("Acme Ltd")).toBeInTheDocument();
    expect(
      timeline.compareDocumentPosition(attack) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

  it("shows ATT&CK context that rests on the follow-up answer the analysis recorded", () => {
    render(<AnalysisDetails />);

    const attack = within(screen.getByRole("region", { name: "Technical Context" }));
    expect(
      attack.getByRole("heading", { name: "Exploit Public-Facing Application" }),
    ).toBeInTheDocument();
    expect(attack.getByText(`“${answer}”`)).toBeInTheDocument();
    expect(attack.getByText("Follow-up answer QA-01")).toBeInTheDocument();
  });

  it("shows nothing of the analysis while the case sources cannot be loaded", () => {
    sourcesState.failed = true;
    const { container } = render(<AnalysisDetails />);

    expect(container).toBeEmptyDOMElement();
  });
});
