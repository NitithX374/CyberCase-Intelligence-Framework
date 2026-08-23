import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ChatReportView } from "@/components/report/ChatReportView";
import * as api from "@/lib/api";

function sampleReport(): api.ChatReportRead {
  return {
    report_id: "report-1",
    thread_id: "thread-1",
    version_number: 1,
    idempotency_key: "report-req-1",
    source_snapshot_hash: "hash-1",
    analysis_message_id: "msg-1",
    retrieval_context_id: "rc-1",
    prompt_version: "deterministic_raw_evidence_report_v1",
    provider: "deterministic",
    model: "template",
    decoding_settings: {},
    persistence_status: "completed",
    validation_status: "validated",
    report: {
      report_version: "preliminary_analysis_report_v1",
      status: "provisional_unverified",
      title: "Case Analysis Report Alpha",
      sections: [],
      claims: [],
      limitations: [],
    },
    validation_errors: [],
    failure_code: null,
    failure_message: null,
    created_at: "2026-08-23T10:00:00Z",
    finished_at: "2026-08-23T10:00:01Z",
    latency_ms: 1,
    input_tokens: 1,
    output_tokens: 1,
  };
}

describe("ChatReportView component", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.restoreAllMocks();
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    if (typeof window !== "undefined") {
      window.URL.createObjectURL = vi.fn(() => "blob:http://localhost/test-blob");
      window.URL.revokeObjectURL = vi.fn();
    }
  });

  it("renders Generate report button when no reports exist", async () => {
    vi.spyOn(api, "listChatReports").mockResolvedValue([]);

    render(
      <QueryClientProvider client={queryClient}>
        <ChatReportView
          threadId="thread-1"
          threadTitle="Incident Alpha"
          threadStatus="answered"
          hasMessages={true}
          hasCompletedAnalysis={true}
          onOpenChat={vi.fn()}
        />
      </QueryClientProvider>,
    );

    expect(await screen.findByRole("button", { name: "Generate report" })).toBeInTheDocument();
    expect(screen.getByText("Case Analysis Report")).toBeInTheDocument();
    expect(screen.queryByText(/retrieval-1/i)).not.toBeInTheDocument();
  });

  it("renders Generate new version button and PDF preview when a report exists", async () => {
    vi.spyOn(api, "listChatReports").mockResolvedValue([sampleReport()]);
    vi.spyOn(api, "downloadChatReportPdf").mockResolvedValue(
      new Blob(["%PDF-1.4 test"], { type: "application/pdf" }),
    );

    render(
      <QueryClientProvider client={queryClient}>
        <ChatReportView
          threadId="thread-1"
          threadTitle="Incident Alpha"
          threadStatus="answered"
          hasMessages={true}
          hasCompletedAnalysis={true}
          onOpenChat={vi.fn()}
        />
      </QueryClientProvider>,
    );

    expect(await screen.findByRole("button", { name: "Generate new version" })).toBeInTheDocument();
    expect(screen.getByText("Version 1 · Saved")).toBeInTheDocument();
    expect(screen.getByText("Case Analysis Report Alpha")).toBeInTheDocument();
  });
});
