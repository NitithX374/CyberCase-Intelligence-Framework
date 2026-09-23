import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { CaseReportView } from "@/components/report/CaseReportView";
import type { CaseAnalysisResultRead, CaseReport } from "@/lib/api";
import * as api from "@/lib/api";

const analysis: CaseAnalysisResultRead = {
  id: "analysis-1",
  case_id: "case-1",
  source_revision: 1,
  schema_version: "case_analysis_trace_v1",
  status: "validated",
  answer: "",
  summary: "",
  trace_json: null,
  retrieval_context_id: null,
  pipeline_config: {},
  external_context_json: {},
  created_at: "2026-09-10T00:00:00Z",
  freshness: "current",
};

function report(version: number): CaseReport {
  return {
    report_id: `report-${version}`,
    case_id: "case-1",
    version_number: version,
    analysis_result_id: "analysis-1",
    report: {
      report_version: "preliminary_analysis_report_v1",
      status: "provisional_unverified",
      title: "Traceable report",
      sections: [],
      claims: [],
      limitations: [],
    },
    created_at: "2026-09-20T00:00:00Z",
  };
}

function renderView() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={queryClient}>
      <CaseReportView caseId="case-1" caseTitle="Investigation" analysisResult={analysis} />
    </QueryClientProvider>,
  );
}

describe("CaseReportView", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    window.URL.createObjectURL = vi.fn(() => "blob:http://localhost/report");
    window.URL.revokeObjectURL = vi.fn();
    vi.spyOn(api, "downloadCaseReportHtml").mockResolvedValue(
      new Blob(["<p>report</p>"], { type: "text/html" }),
    );
  });

  it("offers to generate the first report", async () => {
    vi.spyOn(api, "listCaseReports").mockResolvedValue([]);
    const generate = vi.spyOn(api, "generateCaseReport").mockResolvedValue(report(1));
    renderView();

    expect(await screen.findByRole("heading", { name: "No report yet" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Generate report" }));

    await waitFor(() =>
      expect(generate).toHaveBeenCalledWith("case-1", { analysis_result_id: "analysis-1" }),
    );
    expect(await screen.findByRole("article", { name: "Persisted report" })).toBeInTheDocument();
  });

  it("keeps the version, its status and the download in one header", async () => {
    vi.spyOn(api, "listCaseReports").mockResolvedValue([report(2), report(1)]);
    const download = vi
      .spyOn(api, "downloadCaseReportPdf")
      .mockResolvedValue(new Blob(["%PDF"], { type: "application/pdf" }));
    renderView();

    expect(await screen.findByText("Provisional")).toBeInTheDocument();
    const versions = screen.getByRole("combobox", { name: "Report version" });
    expect(versions).toHaveValue("report-2");

    fireEvent.change(versions, { target: { value: "report-1" } });
    fireEvent.click(screen.getByRole("button", { name: "Download PDF" }));
    await waitFor(() => expect(download).toHaveBeenCalledWith("case-1", "report-1"));
  });
});
