import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import axios from "axios";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { CaseReportView } from "./CaseReportView";
import type { CaseAnalysisResultRead, CaseReport } from "@/lib/api";
import * as api from "@/lib/api";
import { blobRefusal, networkError, refusal } from "@/test/httpErrors";

const analysis: CaseAnalysisResultRead = {
  id: "analysis-1",
  case_id: "case-1",
  source_revision: 1,
  schema_version: "case_analysis_trace_v1",
  status: "validated",
  summary: "",
  trace_json: null,
  retrieval_context_id: null,
  pipeline_config: {},
  external_context_json: {},
  created_at: "2026-09-10T00:00:00Z",
  freshness: "current",
};

function report(version: number, analysisResultId = "analysis-1"): CaseReport {
  return {
    report_id: `report-${version}`,
    case_id: "case-1",
    version_number: version,
    analysis_result_id: analysisResultId,
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
      <CaseReportView caseId="case-1" analysisResult={analysis} />
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

  afterEach(() => {
    vi.unstubAllEnvs();
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

  it("offers no new version once this analysis has its report", async () => {
    vi.spyOn(api, "listCaseReports").mockResolvedValue([report(1)]);
    renderView();

    expect(await screen.findByRole("button", { name: "Download PDF" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "New version" })).not.toBeInTheDocument();
  });

  it("offers a new version when only an older analysis has a report", async () => {
    vi.spyOn(api, "listCaseReports").mockResolvedValue([report(1, "analysis-0")]);
    const generate = vi.spyOn(api, "generateCaseReport").mockResolvedValue(report(2));
    renderView();

    fireEvent.click(await screen.findByRole("button", { name: "New version" }));

    await waitFor(() =>
      expect(generate).toHaveBeenCalledWith("case-1", { analysis_result_id: "analysis-1" }),
    );
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: "New version" })).not.toBeInTheDocument(),
    );
  });

  it("shows the reason a report was refused, and does not offer to retry it", async () => {
    vi.spyOn(api, "listCaseReports").mockResolvedValue([]);
    vi.spyOn(api, "generateCaseReport").mockRejectedValue(
      refusal(409, "report_sources_missing", "The analysis did not record the sources it read"),
    );
    renderView();

    fireEvent.click(await screen.findByRole("button", { name: "Generate report" }));

    const dialog = await screen.findByRole("dialog");
    expect(dialog).toHaveTextContent("The analysis did not record the sources it read");
    expect(screen.queryByRole("button", { name: "ลองอีกครั้ง" })).not.toBeInTheDocument();
    fireEvent.click(screen.getAllByRole("button", { name: /ปิด/ })[0]);
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("shows the reason a PDF download was refused", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000");
    vi.spyOn(api, "listCaseReports").mockResolvedValue([report(1)]);
    const get = vi
      .spyOn(axios, "get")
      .mockRejectedValue(
        blobRefusal(
          409,
          "analysis_source_snapshot_missing",
          "The analysis did not record the sources it read",
        ),
      );
    renderView();

    fireEvent.click(await screen.findByRole("button", { name: "Download PDF" }));

    const dialog = await screen.findByRole("dialog");
    expect(get).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/cases/case-1/reports/report-1/pdf",
      expect.objectContaining({ responseType: "blob" }),
    );
    expect(dialog).toHaveTextContent("The analysis did not record the sources it read");
    expect(dialog).toHaveTextContent("Reason: analysis_source_snapshot_missing");
    expect(screen.queryByRole("button", { name: "ลองอีกครั้ง" })).not.toBeInTheDocument();
  });

  it("shows a failed report list in place, with no modal to be stuck behind", async () => {
    const list = vi
      .spyOn(api, "listCaseReports")
      .mockRejectedValueOnce(networkError())
      .mockResolvedValueOnce([report(1)]);
    renderView();

    expect(
      await screen.findByRole("heading", { name: "Reports could not be loaded" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Generate report" })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Try again" }));

    expect(await screen.findByRole("article", { name: "Persisted report" })).toBeInTheDocument();
    expect(list).toHaveBeenCalledTimes(2);
  });
});
