"use client";

import { useEffect, useState } from "react";
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
  const [reports, setReports] = useState<ChatReportRead[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(threadId));
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    if (!threadId) {
      return;
    }

    const controller = new AbortController();

    void (async () => {
      try {
        const items = await listChatReports(threadId, controller.signal);
        if (controller.signal.aborted) return;
        setReports(items);
        setSelectedReportId(items[0]?.report_id ?? null);
      } catch (error: unknown) {
        if (controller.signal.aborted) return;
        setLoadError(
          getApiErrorMessage(
            error,
            "Could not load persisted reports for this chat thread.",
          ),
        );
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    })();

    return () => {
      controller.abort();
    };
  }, [threadId]);

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
    setIsGenerating(true);
    setGenerationError(null);

    try {
      const report = await generateChatReport(threadId, reportRequestKey());
      setReports((current) => [
        report,
        ...current.filter((item) => item.report_id !== report.report_id),
      ]);
      setSelectedReportId(report.report_id);
    } catch (error: unknown) {
      setGenerationError(
        getApiErrorMessage(
          error,
          "Failed to generate report. Please review the case details and try again.",
        ),
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadPdf = async (report: ChatReportRead) => {
    if (!threadId || isDownloading) return;
    setIsDownloading(true);
    setDownloadError(null);
    try {
      const blob = await downloadChatReportPdf(threadId, report.report_id);
      const blobUrl = window.URL.createObjectURL(blob);
      const downloadLink = document.createElement("a");
      downloadLink.href = blobUrl;
      downloadLink.download = `CyberCase-Report-v${report.version_number}.pdf`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      downloadLink.removeChild(downloadLink);
      window.URL.revokeObjectURL(blobUrl);
    } catch (error: unknown) {
      setDownloadError(
        getApiErrorMessage(
          error,
          "Failed to download the PDF report. Please try again.",
        ),
      );
    } finally {
      setIsDownloading(false);
    }
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
                onDownloadPdf={() => void handleDownloadPdf(selectedReport)}
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
