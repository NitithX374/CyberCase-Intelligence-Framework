import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { CaseReportView } from "./CaseReportView";
import type { CaseReportRead } from "@/lib/api";
import * as api from "@/lib/api";
import { analysisResult } from "@/test/fixtures";
import { blobRefusal, networkError, refusal, timeoutError } from "@/test/httpErrors";

const analysis = analysisResult({ id: "analysis-1", case_id: "case-1" });

function report(version: number, analysisResultId = "analysis-1"): CaseReportRead {
  return {
    report_id: `report-${version}`,
    case_id: "case-1",
    version_number: version,
    analysis_result_id: analysisResultId,
    report: {
      version: "case_report_content_v1",
      title: "Traceable report",
      summary: "",
      techniques_matched: false,
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

  it("previews the saved report as the backend rendered it", async () => {
    vi.spyOn(api, "listCaseReports").mockResolvedValue([report(1)]);
    renderView();

    const preview = await screen.findByTitle("Case report: Traceable report");
    expect(preview).toHaveAttribute("src", "blob:http://localhost/report");
    expect(api.downloadCaseReportHtml).toHaveBeenCalledWith("case-1", "report-1");
  });

  it("explains a preview that timed out, and loads it again on request", async () => {
    vi.spyOn(api, "listCaseReports").mockResolvedValue([report(1)]);
    const preview = vi.spyOn(api, "downloadCaseReportHtml").mockRejectedValue(timeoutError());
    renderView();

    expect(
      await screen.findByRole("heading", { name: "การดำเนินการใช้เวลานานกว่าที่กำหนด" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/timeout of 15000ms exceeded/)).toBeInTheDocument();
    expect(screen.getByText("ไม่สามารถแสดงตัวอย่างรายงานได้")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "โหลดตัวอย่างรายงานใหม่" }));
    await waitFor(() => expect(preview).toHaveBeenCalledTimes(2));
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

  it("shows the backend's reason for a refusal it has no Thai wording for, and offers no retry", async () => {
    vi.spyOn(api, "listCaseReports").mockResolvedValue([]);
    vi.spyOn(api, "generateCaseReport").mockRejectedValue(
      refusal(
        409,
        "case_analysis_unavailable",
        "Only a validated Case analysis can produce a report",
      ),
    );
    renderView();

    fireEvent.click(await screen.findByRole("button", { name: "Generate report" }));

    const dialog = await screen.findByRole("dialog");
    expect(dialog.querySelector("#meaningful-error-message")).toHaveTextContent(
      "Only a validated Case analysis can produce a report",
    );
    expect(screen.queryByRole("button", { name: "ลองอีกครั้ง" })).not.toBeInTheDocument();
    fireEvent.click(screen.getAllByRole("button", { name: /ปิด/ })[0]);
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("says in Thai why a PDF download was refused", async () => {
    vi.spyOn(api, "listCaseReports").mockResolvedValue([report(1)]);
    const get = vi
      .spyOn(api.http, "get")
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
      "/cases/case-1/reports/report-1/pdf",
      expect.objectContaining({ responseType: "blob" }),
    );
    expect(dialog.querySelector("#meaningful-error-message")).toHaveTextContent(
      "การวิเคราะห์นี้ไม่ได้บันทึกแหล่งข้อมูลที่ใช้",
    );
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

  it("says in Thai when a stored report is in a format that can no longer be shown", async () => {
    vi.spyOn(api, "listCaseReports").mockRejectedValue(
      refusal(
        409,
        "case_report_outdated",
        "This report was stored in an older format and can no longer be shown",
      ),
    );
    renderView();

    expect(
      await screen.findByText("รายงานนี้ถูกบันทึกในรูปแบบเก่า จึงไม่สามารถแสดงได้อีกต่อไป"),
    ).toBeInTheDocument();
  });
});
