import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PersistedReportCard } from "@/components/report/PersistedReportCard";
import type { CaseReport } from "@/lib/api";
import * as api from "@/lib/api";

function sampleReport(): CaseReport {
  return {
    report_id: "report-1",
    case_id: "case-1",
    version_number: 1,
    analysis_result_id: "analysis-result-1",
    report: {
      report_version: "preliminary_analysis_report_v1",
      status: "provisional_unverified",
      title: "Traceable report",
      sections: [
        {
          section_id: "case_summary",
          heading: "5.1 สรุปคดี",
          paragraphs: ["Reported findings remain unverified."],
          items: [],
        },
      ],
      claims: [
        {
          claim_id: "C-001",
          section_id: "case_summary",
          text: "A login event was reported.",
          support_type: "user_reported",
          source_ids: [],
          mitre_technique_ids: [],
        },
      ],
      limitations: ["This report is provisional and unverified."],
    },
    created_at: "2026-08-20T00:00:00Z",
  };
}

describe("PersistedReportCard with Jinja2 HTML Viewer", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.restoreAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
    if (typeof window !== "undefined") {
      window.URL.createObjectURL = vi.fn(() => "blob:http://localhost/test-html-blob");
      window.URL.revokeObjectURL = vi.fn();
    }
  });

  it("renders the readable HTML report viewer and does not include claim inspector", async () => {
    const fakeBlob = new Blob(["<!doctype html><title>test</title>"], { type: "text/html" });
    vi.spyOn(api, "downloadCaseReportHtml").mockResolvedValue(fakeBlob);

    render(
      <QueryClientProvider client={queryClient}>
        <PersistedReportCard
          report={sampleReport()}
          caseId="case-1"
          caseTitle="Investigation"
          isDownloading={false}
          onDownloadPdf={vi.fn()}
        />
      </QueryClientProvider>,
    );

    expect(screen.getByText("Version 1 · Saved")).toBeInTheDocument();
    expect(screen.getByText("Traceable report")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Download PDF" })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByLabelText("HTML Report Viewer")).toBeInTheDocument();
    });

    const iframe = screen.getByTitle("Case report: Traceable report");
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute("src", "blob:http://localhost/test-html-blob");

    expect(screen.queryByText("Claim inspector")).not.toBeInTheDocument();
  });

  it("shows MeaningfulErrorModal on report preview failure without raw inline error and retries preview", async () => {
    const downloadSpy = vi
      .spyOn(api, "downloadCaseReportHtml")
      .mockRejectedValue(new Error("timeout of 15000ms exceeded"));

    render(
      <QueryClientProvider client={queryClient}>
        <PersistedReportCard
          report={sampleReport()}
          caseId="case-1"
          caseTitle="Investigation"
          isDownloading={false}
          onDownloadPdf={vi.fn()}
        />
      </QueryClientProvider>,
    );

    expect(
      await screen.findByRole("heading", { name: "การดำเนินการใช้เวลานานกว่าที่กำหนด" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/ระบบยังไม่สามารถยืนยันผลลัพธ์ได้ในขณะนี้/)).toBeInTheDocument();

    expect(screen.getByText("Technical details")).toBeInTheDocument();
    expect(screen.getByText(/timeout of 15000ms exceeded/)).toBeInTheDocument();

    expect(screen.getByText("ไม่สามารถแสดงตัวอย่างรายงานได้")).toBeInTheDocument();

    const retryBtn = screen.getByRole("button", { name: "โหลดตัวอย่างรายงานใหม่" });
    fireEvent.click(retryBtn);
    await waitFor(() => {
      expect(downloadSpy).toHaveBeenCalledTimes(2);
    });
  });
});
