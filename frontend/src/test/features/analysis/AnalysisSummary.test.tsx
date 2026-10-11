import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AnalysisSummary } from "@/features/analysis/AnalysisSummary";
import { useCaseReports } from "@/features/reports/queries";
import type { CaseReportRead } from "@/lib/api/types";
import {
  analysisId,
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
    claims: [
      claim("Room 402 was entered with a hidden key.", source.id),
      claim("Room 503 was forced open with a screwdriver.", source.id, {
        claim_id: "A-02",
        epistemic_status: "not_confirmed",
        supporting_citations: [],
      }),
    ],
    involved_parties: [
      { name: "Tenant A", role: "Suspect", claim_ids: ["A-01"] },
      { name: "Tenant B", role: "Complainant", claim_ids: ["A-01"] },
      { name: "Tenant C", role: "Victim", claim_ids: ["A-02"] },
      { name: "Officer D", role: "Investigator", claim_ids: [] },
    ],
    timeline: [
      { time: "4 May", event: "Room 402 was entered.", claim_ids: ["A-01"] },
      { time: "20 December", event: "Room 503 was forced open.", claim_ids: ["A-02"] },
      { time: "31 January", event: "The file went to the prosecutor.", claim_ids: [] },
    ],
    impacts: [{ description: "8,000 baht and 13 amulets were taken.", claim_ids: ["A-01"] }],
    gaps: [
      {
        gap_id: "G-01",
        gap_key: "how_much",
        topic: "how_much",
        status: "NOT_PROVIDED",
        description: "The total value taken from room 503 is unknown.",
        reason: "The value decides the charge.",
        priority: "medium",
        askable: true,
      },
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

function report(overrides: Partial<CaseReportRead> = {}): CaseReportRead {
  return {
    report_id: "report-1",
    version_number: 1,
    case_id: caseId,
    analysis_result_id: analysisId,
    report: {} as CaseReportRead["report"],
    created_at: "2026-09-28T00:00:00Z",
    ...overrides,
  };
}

function row(label: string) {
  return screen.getByText(label, { selector: "dt" }).nextElementSibling as HTMLElement;
}

const base = `/case/${caseId}/analysis`;

beforeEach(() => {
  vi.mocked(useCaseReports).mockReturnValue({ data: [] } as never);
});

describe("AnalysisSummary", () => {
  it("opens with the summary the analysis wrote, plain when it has no units", () => {
    render(<AnalysisSummary />);

    expect(screen.getByRole("heading", { name: "Summary" })).toBeInTheDocument();
    expect(screen.getByText(summary)).toBeInTheDocument();
  });

  it("names the first parties and links the rest", () => {
    render(<AnalysisSummary />);

    const parties = row("Parties");
    expect(parties).toHaveTextContent("Tenant A");
    expect(parties).toHaveTextContent("Tenant C");
    expect(parties).not.toHaveTextContent("Officer D");
    expect(within(parties).getByRole("link", { name: "All 4 parties" })).toHaveAttribute(
      "href",
      `${base}/details`,
    );
  });

  it("shows where the timeline starts and ends", () => {
    render(<AnalysisSummary />);

    const events = row("From first to last");
    expect(events).toHaveTextContent("Room 402 was entered.");
    expect(events).toHaveTextContent("The file went to the prosecutor.");
    expect(events).not.toHaveTextContent("Room 503 was forced open.");
    expect(within(events).getByRole("link", { name: "All 3 events" })).toBeInTheDocument();
    expect(row("Impact")).toHaveTextContent("8,000 baht and 13 amulets were taken.");
  });

  it("counts the findings by status and links the ones not confirmed", () => {
    render(<AnalysisSummary />);

    const findings = row("Findings");
    expect(findings).toHaveTextContent("2 findings, 1 reported, 1 not confirmed");
    expect(within(findings).getByRole("link", { name: "2 findings" })).toHaveAttribute(
      "href",
      `${base}/findings`,
    );
    expect(within(findings).getByRole("link", { name: "1 not confirmed" })).toHaveAttribute(
      "href",
      `${base}/findings?status=not_confirmed`,
    );
  });

  it("says what is still missing and what ATT&CK found", () => {
    render(<AnalysisSummary />);

    expect(row("Open questions")).toHaveTextContent(
      "The total value taken from room 503 is unknown.",
    );
    expect(row("ATT&CK")).toHaveTextContent("Not applicable");
  });

  it("offers a report when there is none, and says which analysis the latest one came from", () => {
    const { unmount } = render(<AnalysisSummary />);
    expect(row("Report")).toHaveTextContent("No report yet.");
    expect(within(row("Report")).getByRole("link", { name: "Generate a report" })).toHaveAttribute(
      "href",
      `/case/${caseId}/report`,
    );
    unmount();

    vi.mocked(useCaseReports).mockReturnValue({
      data: [report({ version_number: 2, analysis_result_id: "earlier-analysis" })],
    } as never);
    render(<AnalysisSummary />);
    expect(row("Report")).toHaveTextContent("Version 2, from an earlier analysis");
  });
});
