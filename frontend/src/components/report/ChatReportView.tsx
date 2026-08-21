"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useState } from "react";
import {
  downloadChatReportPdf,
  generateChatReport,
  getApiErrorMessage,
  listChatReports,
  type ChatReportRead,
  type ThreadStatus,
} from "@/lib/api";
import { PersistedReportCard } from "./PersistedReportCard";
import { NoSavedReport, ReportVersionHistory } from "./ReportHistory";
import { chatQueryKeys } from "@/lib/query-keys";

interface ChatReportViewProps {
  threadId: string | null;
  threadTitle: string;
  threadStatus: ThreadStatus | null;
  hasMessages: boolean;
  hasValidatedExtraction: boolean;
  onOpenChat: () => void;
}

export function ChatReportView({
  threadId,
  threadTitle,
  threadStatus,
  hasMessages,
  hasValidatedExtraction,
  onOpenChat,
}: ChatReportViewProps) {
  const queryClient = useQueryClient();
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const reportsQuery = useQuery({
    queryKey: threadId ? chatQueryKeys.reports(threadId) : chatQueryKeys.all,
    queryFn: ({ signal }) => listChatReports(threadId!, signal),
    enabled: threadId !== null,
    retry: false,
  });
  const generateMutation = useMutation({
    mutationFn: ({ threadId: targetThreadId, idempotencyKey }: {
      threadId: string;
      idempotencyKey?: string;
    }) => generateChatReport(targetThreadId, idempotencyKey),
    onSuccess: (report, variables) => {
      queryClient.setQueryData<ChatReportRead[]>(
        chatQueryKeys.reports(variables.threadId),
        (current) => [
          report,
          ...(current ?? []).filter((item) => item.report_id !== report.report_id),
        ],
      );
      setSelectedReportId(report.report_id);
    },
  });
  const downloadMutation = useMutation({
    mutationFn: ({ threadId: targetThreadId, report }: {
      threadId: string;
      report: ChatReportRead;
    }) => downloadChatReportPdf(targetThreadId, report.report_id),
    onSuccess: (blob, variables) => {
      downloadPdf(blob, variables.report.version_number);
    },
  });

  const reports = reportsQuery.data ?? [];
  const isLoading = Boolean(threadId) && reportsQuery.isLoading;
  const isGenerating = generateMutation.isPending;
  const isDownloading = downloadMutation.isPending;
  const loadError = reportsQuery.error
    ? getApiErrorMessage(
      reportsQuery.error,
      "Could not load persisted reports for this chat thread.",
    )
    : null;
  const generationError = generateMutation.error
    ? getApiErrorMessage(
      generateMutation.error,
      "Failed to generate report. Please review the case details and try again.",
    )
    : null;
  const downloadError = downloadMutation.error
    ? getApiErrorMessage(
      downloadMutation.error,
      "Failed to download the PDF report. Please try again.",
    )
    : null;

  const selectedReport =
    reports.find((report) => report.report_id === selectedReportId) ??
    reports[0] ??
    null;

  const canGenerate =
    Boolean(threadId) &&
    hasMessages &&
    hasValidatedExtraction &&
    threadStatus !== "processing" &&
    threadStatus !== "awaiting_followup" &&
    threadStatus !== "failed" &&
    !isGenerating;

  const handleGenerate = async () => {
    if (!threadId || !canGenerate) return;
    await generateMutation.mutateAsync({
      threadId,
      idempotencyKey: reportRequestKey(),
    }).catch(() => undefined);
  };

  const handleDownloadPdf = (report: ChatReportRead) => {
    if (!threadId || isDownloading) return;
    downloadMutation.mutate({ threadId, report });
  };

  if (!threadId) {
    return (
      <section
        id="workspace-report-panel"
        role="tabpanel"
        aria-label="Report generation"
        className="min-h-0 flex-1 overflow-y-auto bg-canvas px-4 py-8 sm:px-7 lg:px-10"
      >
        <div className="mx-auto max-w-2xl rounded-2xl border border-dashed border-line-strong bg-surface p-6 sm:p-8">
          <h2 className="text-xl font-extrabold tracking-tight text-ink">
            Select a saved chat
          </h2>
          <p className="mt-3 text-sm leading-6 text-ink-secondary">
            Start or open a chat before generating a persistent report.
          </p>
          <button
            type="button"
            onClick={onOpenChat}
            className="mt-6 inline-flex min-h-11 items-center rounded-xl bg-primary px-4 text-sm font-bold text-ivory outline-none transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
          >
            Return to Chat
          </button>
        </div>
      </section>
    );
  }

  return (
    <section
      id="workspace-report-panel"
      role="tabpanel"
      aria-label="Report generation"
      className="min-h-0 flex-1 overflow-y-auto bg-canvas px-4 py-8 sm:px-7 lg:px-10"
    >
      <div className="mx-auto w-full max-w-[1080px]">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-ink-secondary">
              Executive Briefing
            </p>
            <h1 className="mt-3 text-3xl font-extrabold tracking-[-0.035em] text-ink sm:text-4xl">
              Digital-forensics report
            </h1>
            <p className="mt-4 text-sm leading-6 text-ink-secondary sm:text-base sm:leading-7">
              Generate a structured intelligence report from this chat&apos;s
              case details, extracted evidence, and MITRE mapping findings.
            </p>
          </div>
          <span className="rounded-full border border-line-strong bg-surface px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.12em] text-ink-secondary">
            Provisional / Unverified
          </span>
        </div>

        <div className="mt-7 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => void handleGenerate()}
            disabled={!canGenerate}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-primary px-4 text-sm font-bold text-ivory outline-none transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled"
          >
            {isGenerating && (
              <span
                className="h-4 w-4 animate-spin rounded-full border-2 border-ivory/40 border-t-ivory"
                aria-hidden="true"
              />
            )}
            {isGenerating ? "Generating report..." : "Generate report"}
          </button>
          <button
            type="button"
            onClick={onOpenChat}
            className="inline-flex min-h-11 items-center rounded-xl border border-line-strong bg-surface px-4 text-sm font-bold text-ink outline-none transition-colors hover:border-primary hover:bg-surface-hover active:bg-control-disabled focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
          >
            Return to Chat
          </button>
        </div>

        <div className="mt-5 rounded-xl border border-line bg-surface px-4 py-3 text-sm leading-6 text-ink-secondary">
          {readinessMessage({
            hasMessages,
            hasValidatedExtraction,
            threadId,
            threadStatus,
          })}
        </div>

        {loadError && <InlineError message={loadError} />}
        {generationError && <InlineError message={generationError} />}
        {downloadError && <InlineError message={downloadError} />}

        {isLoading ? (
          <div className="mt-8 rounded-2xl border border-line bg-surface p-6 text-center text-sm font-medium text-ink-secondary">
            Loading saved report history...
          </div>
        ) : reports.length > 0 ? (
          <div className="mt-8 grid gap-6 lg:grid-cols-[260px_minmax(0,1fr)]">
            <ReportVersionHistory
              reports={reports}
              selectedReportId={selectedReport?.report_id ?? null}
              onSelect={setSelectedReportId}
            />
            {selectedReport && (
              <PersistedReportCard
                key={selectedReport.report_id}
                report={selectedReport}
                threadId={threadId}
                threadTitle={threadTitle}
                isDownloading={isDownloading}
                onDownloadPdf={() => handleDownloadPdf(selectedReport)}
              />
            )}
          </div>
        ) : (
          <NoSavedReport />
        )}
      </div>
    </section>
  );
}

function InlineError({ message }: { message: string }) {
  return (
    <div className="mt-5 rounded-xl border border-[#F0B8B2] bg-[#FFF6F4] px-4 py-3 text-sm leading-6 text-[#B42318]">
      {message}
    </div>
  );
}

function readinessMessage({
  hasMessages,
  hasValidatedExtraction,
  threadId,
  threadStatus,
}: {
  hasMessages: boolean;
  hasValidatedExtraction: boolean;
  threadId: string | null;
  threadStatus: ThreadStatus | null;
}): string {
  if (!threadId || !hasMessages) {
    return "A chat investigation is required before a report can be generated.";
  }
  if (threadStatus === "processing") {
    return "The investigation is still processing. Please wait for completion before generating a report.";
  }
  if (threadStatus === "awaiting_followup") {
    return "Answer the pending clarification in Chat before generating a report.";
  }
  if (threadStatus === "failed") {
    return "The latest chat response failed. Resolve it before generating a report.";
  }
  if (!hasValidatedExtraction) {
    return "A validated case analysis is not available yet. Complete the chat investigation first.";
  }
  return "Ready. Generate a structured intelligence report from this case snapshot.";
}

function reportRequestKey(): string | undefined {
  if (typeof globalThis.crypto?.randomUUID === "function") {
    return globalThis.crypto.randomUUID();
  }
  return `report-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function downloadPdf(blob: Blob, versionNumber: number): void {
  const blobUrl = window.URL.createObjectURL(blob);
  const downloadLink = document.createElement("a");
  downloadLink.href = blobUrl;
  downloadLink.download = `CyberCase-Report-v${versionNumber}.pdf`;
  document.body.appendChild(downloadLink);
  downloadLink.click();
  downloadLink.remove();
  window.URL.revokeObjectURL(blobUrl);
}
