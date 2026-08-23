import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PersistedReportCard } from "@/components/report/PersistedReportCard";
import type { ChatReportRead } from "@/lib/api";
import * as api from "@/lib/api";

function sampleReport(): ChatReportRead {
  return {
    report_id: "report-1",
    thread_id: "thread-1",
    version_number: 1,
    idempotency_key: "report-request-1",
    source_snapshot_hash: "snapshot-1",
    analysis_message_id: "analysis-message-1",
    retrieval_context_id: "retrieval-1",
    prompt_version: "deterministic_raw_evidence_report_v1",
    provider: "deterministic",
    model: "template",
    decoding_settings: {},
    persistence_status: "completed",
    validation_status: "validated",
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
          source_message_ids: ["message-1"],
          mitre_technique_ids: [],
        },
      ],
      limitations: ["This report is provisional and unverified."],
    },
    validation_errors: [],
    failure_code: null,
    failure_message: null,
    created_at: "2026-08-20T00:00:00Z",
    finished_at: "2026-08-20T00:00:01Z",
    latency_ms: 1,
    input_tokens: 1,
    output_tokens: 1,
  };
}

describe("PersistedReportCard with Real PDF Viewer", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.restoreAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
    if (typeof window !== "undefined") {
      window.URL.createObjectURL = vi.fn(() => "blob:http://localhost/test-pdf-blob");
      window.URL.revokeObjectURL = vi.fn();
    }
  });

  it("renders the real PDF viewer iframe and does not include claim inspector", async () => {
    const fakeBlob = new Blob(["%PDF-1.4 test"], { type: "application/pdf" });
    vi.spyOn(api, "downloadChatReportPdf").mockResolvedValue(fakeBlob);

    render(
      <QueryClientProvider client={queryClient}>
        <PersistedReportCard
          report={sampleReport()}
          threadId="thread-1"
          threadTitle="Investigation"
          isDownloading={false}
          onDownloadPdf={vi.fn()}
        />
      </QueryClientProvider>,
    );

    expect(screen.getByText("Version 1 · Saved")).toBeInTheDocument();
    expect(screen.getByText("Traceable report")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Download PDF" })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByLabelText("PDF Document Viewer")).toBeInTheDocument();
    });

    const iframe = screen.getByTitle("PDF Report: Traceable report");
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute("src", "blob:http://localhost/test-pdf-blob#toolbar=1&navpanes=0");

    expect(screen.queryByText("Claim inspector")).not.toBeInTheDocument();
  });

  it("renders failure details when report persistence status is failed", () => {
    const failedReport = {
      ...sampleReport(),
      persistence_status: "failed" as const,
      report: null,
      failure_message: "Validation schema mismatch occurred during report generation.",
      failure_code: "REPORT_SYNTHESIS_FAILED",
      validation_errors: ["Missing timeline anchor."],
    };

    render(
      <QueryClientProvider client={queryClient}>
        <PersistedReportCard
          report={failedReport}
          threadId="thread-1"
          threadTitle="Investigation"
          isDownloading={false}
          onDownloadPdf={vi.fn()}
        />
      </QueryClientProvider>,
    );

    expect(screen.getByText("Report generation failed")).toBeInTheDocument();
    expect(
      screen.getByText("Validation schema mismatch occurred during report generation."),
    ).toBeInTheDocument();
    expect(screen.getByText("Failure code: REPORT_SYNTHESIS_FAILED")).toBeInTheDocument();
    expect(screen.getByText("Missing timeline anchor.")).toBeInTheDocument();
    expect(screen.queryByLabelText("PDF Document Viewer")).not.toBeInTheDocument();
    expect(screen.queryByText("Claim inspector")).not.toBeInTheDocument();
  });
});
