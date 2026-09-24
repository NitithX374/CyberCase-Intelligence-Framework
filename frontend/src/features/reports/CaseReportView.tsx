"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  downloadCaseReportPdf,
  generateCaseReport,
  listCaseReports,
  type CaseAnalysisResultRead,
  type CaseReport,
} from "@/lib/api";
import { caseQueryKeys } from "@/lib/queryKeys";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
import { toUserFacingError, type UserFacingError } from "@/lib/userFacingError";
import { PersistedReportCard } from "./PersistedReportCard";
import { Icon } from "@/components/icons";
import { EmptyState } from "@/components/EmptyState";
import { formatDate } from "@/lib/format";

interface CaseReportViewProps {
  caseId: string;
  caseTitle: string;
  analysisResult: CaseAnalysisResultRead | null;
}

export function CaseReportView({ caseId, caseTitle, analysisResult }: CaseReportViewProps) {
  const queryClient = useQueryClient();
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const reportsQuery = useQuery({
    queryKey: caseQueryKeys.reports(caseId),
    queryFn: ({ signal }) => listCaseReports(caseId, signal),
    retry: false,
  });
  const generateMutation = useMutation({
    mutationFn: (resultId: string) => generateCaseReport(caseId, { analysis_result_id: resultId }),
    onSuccess: (report) => {
      queryClient.setQueryData<CaseReport[]>(caseQueryKeys.reports(caseId), (current) => [
        report,
        ...(current ?? []).filter((item) => item.report_id !== report.report_id),
      ]);
      setSelectedReportId(report.report_id);
    },
  });
  const downloadMutation = useMutation({
    mutationFn: (report: CaseReport) => downloadCaseReportPdf(caseId, report.report_id),
    onSuccess: (blob, report) => downloadPdf(blob, report.version_number),
  });
  const reports = reportsQuery.data ?? [];
  const selectedReport =
    reports.find((report) => report.report_id === selectedReportId) ?? reports[0] ?? null;
  const canGenerate = Boolean(
    analysisResult?.status === "validated" && !generateMutation.isPending,
  );
  const activeError: UserFacingError | null = useMemo(() => {
    const error = generateMutation.error ?? downloadMutation.error ?? reportsQuery.error;
    return error
      ? toUserFacingError(error, {
          isUncertain: generateMutation.error !== null,
          actionLabel: "ลองอีกครั้ง",
        })
      : null;
  }, [downloadMutation.error, generateMutation.error, reportsQuery.error]);

  const handleGenerate = async () => {
    if (!canGenerate || !analysisResult) return;
    await generateMutation.mutateAsync(analysisResult.id).catch(() => undefined);
  };
  const handleRetry = () => {
    if (generateMutation.error) {
      generateMutation.reset();
      void handleGenerate();
    } else if (downloadMutation.error && selectedReport) {
      downloadMutation.reset();
      downloadMutation.mutate(selectedReport);
    } else if (reportsQuery.error) {
      void reportsQuery.refetch();
    }
  };

  return (
    <section
      id="workspace-report-panel"
      aria-label="Case report"
      className="flex shrink-0 flex-col bg-surface"
    >
      <div className="mx-auto w-full max-w-[52rem] px-5 pt-16 pb-16 sm:px-8">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line pb-3">
          <div className="flex min-w-0 flex-wrap items-center gap-x-2.5 gap-y-1">
            <h2 className="text-base font-semibold text-ink">Report</h2>
            {selectedReport && (
              <>
                <span
                  className="text-[13px] text-unresolved"
                  title="Generated from the analysis. Not yet verified by an analyst."
                >
                  Provisional
                </span>
                {reports.length > 1 ? (
                  <label className="relative inline-flex items-center">
                    <span className="sr-only">Report version</span>
                    <select
                      aria-label="Report version"
                      value={selectedReport.report_id}
                      onChange={(event) => setSelectedReportId(event.target.value)}
                      className="h-7 cursor-pointer appearance-none rounded-md bg-surface-nested py-0 pr-6 pl-2 text-[13px] font-medium text-ink outline-none hover:bg-line"
                    >
                      {reports.map((report, index) => (
                        <option key={report.report_id} value={report.report_id}>
                          Version {report.version_number}
                          {index === 0 ? " (latest)" : ""}
                        </option>
                      ))}
                    </select>
                    <Icon
                      name="chevron"
                      className="pointer-events-none absolute right-1.5 h-3.5 w-3.5 text-ink-muted"
                    />
                  </label>
                ) : (
                  <span className="text-[13px] text-ink-muted">
                    Version {selectedReport.version_number} ·{" "}
                    {formatDate(selectedReport.created_at, "monthDay")}
                  </span>
                )}
              </>
            )}
          </div>
          {selectedReport && (
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => void handleGenerate()}
                disabled={!canGenerate}
                title="Generate a new version from the latest analysis"
                className="btn-ghost h-8 px-2.5"
              >
                <Icon
                  name={generateMutation.isPending ? "spinner" : "refresh"}
                  className="h-4 w-4"
                />
                {generateMutation.isPending ? "Generating…" : "New version"}
              </button>
              <button
                type="button"
                onClick={() => downloadMutation.mutate(selectedReport)}
                disabled={downloadMutation.isPending}
                className="btn-primary h-8 px-3"
              >
                <Icon
                  name={downloadMutation.isPending ? "spinner" : "download"}
                  className="h-4 w-4"
                />
                {downloadMutation.isPending ? "Preparing PDF…" : "Download PDF"}
              </button>
            </div>
          )}
        </header>

        {reportsQuery.isLoading ? (
          <div
            role="status"
            aria-label="Loading reports"
            className="mt-4 h-[420px] animate-pulse rounded-xl bg-surface-nested"
          />
        ) : selectedReport ? (
          <PersistedReportCard
            key={selectedReport.report_id}
            report={selectedReport}
            caseId={caseId}
            caseTitle={caseTitle}
          />
        ) : (
          <NoSavedReport
            canGenerate={canGenerate}
            isGenerating={generateMutation.isPending}
            onGenerate={() => void handleGenerate()}
          />
        )}
      </div>
      <MeaningfulErrorModal
        isOpen={Boolean(activeError)}
        error={activeError}
        onClose={() => {
          generateMutation.reset();
          downloadMutation.reset();
        }}
        onRetry={handleRetry}
      />
    </section>
  );
}

function downloadPdf(blob: Blob, versionNumber: number): void {
  const blobUrl = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = blobUrl;
  link.download = `CyberCase-Report-v${versionNumber}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(blobUrl);
}

function NoSavedReport({
  canGenerate,
  isGenerating,
  onGenerate,
}: {
  canGenerate: boolean;
  isGenerating: boolean;
  onGenerate: () => void;
}) {
  const available = canGenerate || isGenerating;
  return (
    <EmptyState
      title="No report yet"
      titleAs="h3"
      description={
        available
          ? "Turn this analysis into a printable report."
          : "Analyze the case before generating a report."
      }
      className="py-14"
    >
      {available && (
        <button
          type="button"
          onClick={onGenerate}
          disabled={isGenerating}
          className="btn-primary mt-5"
        >
          {isGenerating && <Icon name="spinner" className="h-4 w-4" />}
          {isGenerating ? "Generating…" : "Generate report"}
        </button>
      )}
    </EmptyState>
  );
}
