"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import {
  downloadChatReportPdf,
  type ChatReportRead,
} from "@/lib/api";

interface PersistedReportCardProps {
  report: ChatReportRead;
  threadId: string;
  threadTitle: string;
  isDownloading: boolean;
  onDownloadPdf: () => void;
}

export function PersistedReportCard({
  report,
  threadId,
  threadTitle,
  isDownloading,
  onDownloadPdf,
}: PersistedReportCardProps) {
  return (
    <article
      aria-label="Persisted report"
      className="min-w-0 rounded-2xl border border-line-strong bg-surface p-5 shadow-[0_4px_18px_rgba(39,39,39,0.05)] sm:p-8"
    >
      <header className="border-b border-line pb-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-ink-secondary">
            Version {report.version_number} · Saved
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-line-strong bg-surface px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-[0.12em] text-ink-secondary">
              {report.persistence_status === "completed"
                ? "Provisional / Unverified"
                : "Generation failed"}
            </span>
            {report.persistence_status === "completed" && report.report && (
              <button
                type="button"
                onClick={onDownloadPdf}
                disabled={isDownloading}
                className="rounded-full border border-primary bg-primary px-3 py-1 text-[11px] font-extrabold uppercase tracking-[0.12em] text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed disabled:cursor-wait disabled:border-control-disabled disabled:bg-control-disabled disabled:text-ink-disabled"
              >
                {isDownloading ? "Preparing PDF..." : "Download PDF"}
              </button>
            )}
          </div>
        </div>
        <h2 className="mt-2 text-2xl font-extrabold tracking-[-0.03em] text-ink">
          {report.report?.title ?? threadTitle}
        </h2>
        <p className="mt-2 text-xs text-ink-secondary">
          Retrieval context {report.retrieval_context_id} · {report.model}
        </p>
      </header>

      {report.persistence_status === "failed" || !report.report ? (
        <ReportFailure report={report} />
      ) : (
        <ReportPdfViewer
          threadId={threadId}
          reportId={report.report_id}
          title={report.report.title ?? threadTitle}
        />
      )}
    </article>
  );
}

function ReportPdfViewer({
  threadId,
  reportId,
  title,
}: {
  threadId: string;
  reportId: string;
  title: string;
}) {
  const {
    data: pdfUrl,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["report-pdf-url", threadId, reportId],
    queryFn: async () => {
      const blob = await downloadChatReportPdf(threadId, reportId);
      if (
        typeof window !== "undefined" &&
        typeof window.URL?.createObjectURL === "function"
      ) {
        return window.URL.createObjectURL(blob);
      }
      return null;
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  useEffect(() => {
    return () => {
      if (
        pdfUrl &&
        typeof window !== "undefined" &&
        typeof window.URL?.revokeObjectURL === "function"
      ) {
        window.URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl]);

  if (isLoading) {
    return (
      <div
        aria-label="Loading PDF preview"
        className="mt-6 flex h-[700px] w-full flex-col items-center justify-center rounded-xl border border-dashed border-line-strong bg-surface-nested p-6 text-center text-ink-secondary"
      >
        <div
          className="h-8 w-8 animate-spin rounded-full border-2 border-primary/30 border-t-primary"
          aria-hidden="true"
        />
        <p className="mt-4 text-sm font-semibold text-ink">Loading PDF report...</p>
        <p className="mt-1 text-xs text-ink-secondary">
          Fetching formatted document and security intelligence data.
        </p>
      </div>
    );
  }

  if (error || !pdfUrl) {
    const errorMessage =
      error instanceof Error ? error.message : "Unable to display PDF preview.";
    return (
      <div className="mt-6 rounded-xl border border-[#F0B8B2] bg-[#FFF6F4] p-5 text-sm text-[#B42318]">
        <p className="font-bold">Failed to load PDF preview</p>
        <p className="mt-1 text-xs">{errorMessage}</p>
      </div>
    );
  }

  return (
    <div
      aria-label="PDF Document Viewer"
      className="mt-6 overflow-hidden rounded-xl border border-line-strong bg-surface shadow-sm"
    >
      <iframe
        src={`${pdfUrl}#toolbar=1&navpanes=0`}
        title={`PDF Report: ${title}`}
        className="h-[800px] w-full border-0 bg-canvas"
      />
    </div>
  );
}

function ReportFailure({ report }: { report: ChatReportRead }) {
  return (
    <div className="mt-6 rounded-xl border border-[#F0B8B2] bg-[#FFF6F4] p-4">
      <h3 className="text-sm font-extrabold text-[#B42318]">
        Report generation failed
      </h3>
      <p className="mt-2 text-sm leading-6 text-ink-secondary">
        {report.failure_message ?? "The backend did not produce a validated report."}
      </p>
      {report.failure_code && (
        <p className="mt-2 text-xs font-bold uppercase tracking-[0.1em] text-[#B42318]">
          Failure code: {report.failure_code}
        </p>
      )}
      {report.validation_errors.length > 0 && (
        <ul className="mt-3 list-disc space-y-1 pl-5 text-xs leading-5 text-ink-secondary">
          {report.validation_errors.map((error, index) => (
            <li key={`validation-error-${index}`}>{error}</li>
          ))}
        </ul>
      )}
      <p className="mt-4 text-sm font-semibold text-ink">
        Resolve the issue, then generate another version. This failed attempt is
        preserved in report history.
      </p>
    </div>
  );
}
