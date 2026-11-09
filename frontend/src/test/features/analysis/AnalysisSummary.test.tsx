import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnalysisSummary } from "@/features/analysis/AnalysisSummary";
import {
  analysisResult,
  caseId,
  claim,
  narrativeSource,
  sourcesRead,
  trace,
} from "@/test/fixtures";

const source = narrativeSource("Two rooms were broken into at the dormitory.");
const summary = "Two rooms in one dormitory were broken into by the same tenant.";

const analysis = analysisResult({
  summary,
  trace_json: trace({
    summary,
    claims: [claim("Room 402 was entered with a hidden key.", source.id)],
    involved_parties: [{ name: "Tenant A", role: "Suspect", claim_ids: ["A-01"] }],
    timeline: [{ time: "4 May", event: "Room 402 was entered.", claim_ids: ["A-01"] }],
    impacts: [{ description: "8,000 baht and 13 amulets were taken.", claim_ids: ["A-01"] }],
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

describe("AnalysisSummary", () => {
  it("opens with the summary the analysis wrote, plain when it has no units", () => {
    render(<AnalysisSummary />);

    const heading = screen.getByRole("heading", { name: "What happened" });
    expect(heading.closest("section")).toHaveAttribute("id", "section-summary");
    expect(screen.getByText(summary)).toBeInTheDocument();
  });

  it("keeps to the summary: no glance rows of parties, findings, report or ATT&CK", () => {
    render(<AnalysisSummary />);

    const section = screen.getByRole("heading", { name: "What happened" }).closest("section");
    expect(section?.querySelector("dl")).toBeNull();
    expect(screen.queryByText("At a glance")).not.toBeInTheDocument();
    expect(screen.queryByText("Tenant A")).not.toBeInTheDocument();
    expect(screen.queryByText("ATT&CK")).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Generate a report" })).not.toBeInTheDocument();
  });
});
