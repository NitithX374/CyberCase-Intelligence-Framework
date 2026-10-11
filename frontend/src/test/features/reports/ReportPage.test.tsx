import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ReportPage } from "@/features/reports/ReportPage";
import { analysisResult } from "@/test/fixtures";

const mocks = vi.hoisted(() => ({
  push: vi.fn(),
  refetch: vi.fn(),
  query: {} as Record<string, unknown>,
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ caseId: "case-1" }),
  useRouter: () => ({ push: mocks.push }),
}));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => mocks.query,
}));
vi.mock("@/features/reports/CaseReportView", () => ({
  CaseReportView: ({
    caseId,
    analysisResult: result,
  }: {
    caseId: string;
    analysisResult: { id: string };
  }) => <div data-testid="report-view">{`${caseId}:${result.id}`}</div>,
}));

describe("ReportPage", () => {
  beforeEach(() => {
    mocks.push.mockReset();
    mocks.refetch.mockReset();
    mocks.query = { data: null, isLoading: false, isLoadingError: false, refetch: mocks.refetch };
  });

  it("shows the report of the latest analysis", () => {
    mocks.query = {
      ...mocks.query,
      data: analysisResult({ id: "analysis-1", case_id: "case-1" }),
    };

    render(<ReportPage />);

    expect(screen.getByTestId("report-view")).toHaveTextContent("case-1:analysis-1");
  });

  it("says there is no report before the first analysis, and offers the analysis", () => {
    render(<ReportPage />);

    expect(screen.getByRole("heading", { name: "No report yet" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Open analysis" }));
    expect(mocks.push).toHaveBeenCalledWith("/case/case-1/analysis");
  });

  it("waits while the analysis loads", () => {
    mocks.query = { ...mocks.query, isLoading: true };

    render(<ReportPage />);

    expect(screen.getByRole("status", { name: "Loading report" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "No report yet" })).not.toBeInTheDocument();
  });

  it("offers another try when the analysis could not be read", () => {
    mocks.query = { ...mocks.query, isLoadingError: true };

    render(<ReportPage />);

    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(mocks.refetch).toHaveBeenCalledOnce();
  });
});
