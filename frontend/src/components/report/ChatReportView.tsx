import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  downloadChatReportPdf,
  generateChatReport,
  listChatReports,
  type ChatReportRead,
  type ThreadStatus,
} from "@/lib/api";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError, type UserFacingError } from "@/lib/user-facing-error";
import { PersistedReportCard } from "./PersistedReportCard";
import { NoSavedReport, ReportVersionSelector } from "./ReportHistory";
import { chatQueryKeys } from "@/lib/query-keys";
import { Icon } from "@/components/common/icons";

interface ChatReportViewProps {
  threadId: string | null;
  threadTitle: string;
  threadStatus: ThreadStatus | null;
  hasMessages: boolean;
  hasCompletedAnalysis: boolean;
  onOpenChat: () => void;
  onOpenOverview?: () => void;
}

export function ChatReportView({
  threadId,
  threadTitle,
  threadStatus,
  hasMessages,
  hasCompletedAnalysis,
  onOpenChat,
  onOpenOverview,
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
    mutationFn: ({
      threadId: targetThreadId,
      idempotencyKey,
    }: {
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
    mutationFn: ({
      threadId: targetThreadId,
      report,
    }: {
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

  const activeReportError: UserFacingError | null = useMemo(() => {
    if (generateMutation.error) {
      return toUserFacingError(generateMutation.error, {
        actionLabel: "ลองสร้างรายงานอีกครั้ง",
      });
    }
    if (downloadMutation.error) {
      return toUserFacingError(downloadMutation.error, {
        actionLabel: "ลองดาวน์โหลดอีกครั้ง",
      });
    }
    if (reportsQuery.error) {
      return toUserFacingError(reportsQuery.error, {
        actionLabel: "โหลดใหม่",
      });
    }
    return null;
  }, [generateMutation.error, downloadMutation.error, reportsQuery.error]);

  const handleClearReportError = () => {
    generateMutation.reset();
    downloadMutation.reset();
  };

  const handleRetryReport = () => {
    if (generateMutation.error) {
      generateMutation.reset();
      void handleGenerate();
    } else if (downloadMutation.error && selectedReport) {
      downloadMutation.reset();
      handleDownloadPdf(selectedReport);
    } else if (reportsQuery.error) {
      void reportsQuery.refetch();
    }
  };

  const selectedReport =
    reports.find((report) => report.report_id === selectedReportId) ??
    reports[0] ??
    null;

  const canGenerate =
    Boolean(threadId) &&
    hasMessages &&
    hasCompletedAnalysis &&
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
        aria-label="Case report"
        className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas p-6 sm:p-10"
      >
        <div className="mx-auto max-w-lg rounded-lg border border-dashed border-line bg-surface p-8 text-center space-y-3">
          <h2 className="text-lg font-bold text-ink">
            Select a Case
          </h2>
          <p className="text-xs text-ink-secondary">
            Open or create an investigation case before generating a report.
          </p>
          <div className="pt-2">
            <button
              type="button"
              onClick={onOpenChat}
              className="inline-flex items-center gap-2 rounded bg-primary px-4 py-2 text-xs font-bold text-ivory"
            >
              <span>Return to Case</span>
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section
      id="workspace-report-panel"
      role="tabpanel"
      aria-label="Case report"
      className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas"
    >
      <div className="mx-auto w-full max-w-5xl space-y-6 px-4 py-6 sm:px-8">
        {/* Document-Oriented Dossier Header */}
        <header className="border-b border-line pb-4">
          <div className="flex flex-wrap items-baseline justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] font-bold tracking-widest text-ink-muted uppercase">
                  CASE ANALYSIS REPORT · รายงานวิเคราะห์คดี
                </span>
                <span className="font-mono text-[11px] text-ink-muted">
                  #{threadId.slice(0, 8)}
                </span>
              </div>
              <h1 className="mt-1 text-xl font-bold tracking-tight text-ink sm:text-2xl">
                Case Analysis Report
              </h1>
              <p className="mt-1 text-xs text-ink-secondary">
                Provisional analytical report compiled from submitted case evidence and MITRE ATT&amp;CK threat intelligence.
              </p>
            </div>

            {/* Version Generation & Actions */}
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={() => void handleGenerate()}
                disabled={!canGenerate}
                className="inline-flex items-center gap-2 rounded bg-primary px-4 py-2 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled"
              >
                {isGenerating && (
                  <span
                    className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ivory/40 border-t-ivory"
                    aria-hidden="true"
                  />
                )}
                <span>
                  {isGenerating
                    ? "Generating version..."
                    : reports.length > 0
                      ? "Generate new version"
                      : "Generate report"}
                </span>
              </button>

              <button
                type="button"
                onClick={onOpenOverview ?? onOpenChat}
                className="inline-flex items-center gap-1.5 rounded border border-line bg-surface px-3 py-2 text-xs font-bold text-ink transition-colors hover:border-ink hover:bg-surface-hover"
              >
                <Icon name="overview" className="h-3.5 w-3.5" />
                <span>Case Overview</span>
              </button>
            </div>
          </div>

          {/* Versions Selector row if multiple versions exist */}
          {reports.length > 1 && (
            <div className="mt-3 pt-2 border-t border-line/60">
              <ReportVersionSelector
                reports={reports}
                selectedReportId={selectedReport?.report_id ?? null}
                onSelect={setSelectedReportId}
              />
            </div>
          )}
        </header>

        {/* Primary Content Hero */}
        {isLoading ? (
          <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-line bg-surface p-6 text-xs text-ink-muted">
            <span>Loading case report data...</span>
          </div>
        ) : reports.length > 0 && selectedReport ? (
          <PersistedReportCard
            key={selectedReport.report_id}
            report={selectedReport}
            threadId={threadId}
            threadTitle={threadTitle}
            isDownloading={isDownloading}
            onDownloadPdf={() => handleDownloadPdf(selectedReport)}
          />
        ) : (
          <NoSavedReport
            canGenerate={canGenerate}
            isGenerating={isGenerating}
            onGenerate={() => void handleGenerate()}
            onOpenOverview={onOpenOverview ?? onOpenChat}
          />
        )}
      </div>

      <MeaningfulErrorModal
        isOpen={Boolean(activeReportError)}
        error={activeReportError}
        onClose={handleClearReportError}
        onRetry={handleRetryReport}
      />
    </section>
  );
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
