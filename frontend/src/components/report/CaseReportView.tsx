"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useRef, useState } from "react";
import {
  downloadCaseReportPdf,
  generateCaseReport,
  listCaseReports,
  type CaseAnalysisResultRead,
  type CaseRunRead,
  type ChatReportRead,
} from "@/lib/api";
import { caseQueryKeys } from "@/hooks/useCaseQueries";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError, type UserFacingError } from "@/lib/user-facing-error";
import { PersistedReportCard } from "./PersistedReportCard";
import { NoSavedReport, ReportVersionSelector } from "./ReportHistory";
import { Icon } from "@/components/common/icons";

interface CaseReportViewProps {
  caseId: string;
  caseTitle: string;
  analysisResult: CaseAnalysisResultRead | null;
  runStatus: CaseRunRead["status"] | null;
  onOpenChat: () => void;
  onOpenOverview: () => void;
}

export function CaseReportView({ caseId, caseTitle, analysisResult, runStatus, onOpenChat, onOpenOverview }: CaseReportViewProps) {
  const queryClient = useQueryClient();
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const pendingGenerationRef = useRef<{ caseId: string; resultId: string; idempotencyKey: string } | null>(null);
  const reportsQuery = useQuery({
    queryKey: caseQueryKeys.reports(caseId),
    queryFn: ({ signal }) => listCaseReports(caseId, signal),
    retry: false,
  });
  const generateMutation = useMutation({
    mutationFn: (input: { resultId: string; idempotencyKey: string }) => generateCaseReport(caseId, { analysis_result_id: input.resultId, idempotency_key: input.idempotencyKey }),
    onSuccess: (report) => {
      pendingGenerationRef.current = null;
      queryClient.setQueryData<ChatReportRead[]>(caseQueryKeys.reports(caseId), (current) => [report, ...(current ?? []).filter((item) => item.report_id !== report.report_id)]);
      setSelectedReportId(report.report_id);
    },
  });
  const downloadMutation = useMutation({
    mutationFn: (report: ChatReportRead) => downloadCaseReportPdf(caseId, report.report_id),
    onSuccess: (blob, report) => downloadPdf(blob, report.version_number),
  });
  const reports = reportsQuery.data ?? [];
  const selectedReport = reports.find((report) => report.report_id === selectedReportId) ?? reports[0] ?? null;
  const canGenerate = Boolean(analysisResult?.status === "validated" && runStatus !== "queued" && runStatus !== "running" && !generateMutation.isPending);
  const activeError: UserFacingError | null = useMemo(() => {
    const error = generateMutation.error ?? downloadMutation.error ?? reportsQuery.error;
    return error ? toUserFacingError(error, { isUncertain: generateMutation.error !== null, actionLabel: "ลองอีกครั้ง" }) : null;
  }, [downloadMutation.error, generateMutation.error, reportsQuery.error]);

  const handleGenerate = async () => {
    if (!canGenerate || !analysisResult) return;
    const pending = pendingGenerationRef.current;
    const idempotencyKey = pending?.caseId === caseId && pending.resultId === analysisResult.id ? pending.idempotencyKey : reportRequestKey();
    pendingGenerationRef.current = { caseId, resultId: analysisResult.id, idempotencyKey };
    await generateMutation.mutateAsync({ resultId: analysisResult.id, idempotencyKey }).catch(() => undefined);
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
    <section id="workspace-report-panel" role="tabpanel" aria-label="Case report" className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas">
      <div className="mx-auto w-full max-w-5xl space-y-6 px-4 py-6 sm:px-8">
        <header className="border-b border-line pb-5">
          <div className="flex flex-wrap items-baseline justify-between gap-4">
            <div>
              <p className="section-eyebrow">CASE ANALYSIS REPORT · รายงานวิเคราะห์คดี</p>
              <h1 className="mt-1 text-2xl font-extrabold tracking-[-0.035em] text-ink sm:text-3xl">Case Analysis Report</h1>
              <p className="mt-2 max-w-2xl text-xs leading-relaxed text-ink-secondary">Report versions are bound to the selected Case analysis result and its immutable evidence snapshot.</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button type="button" onClick={() => void handleGenerate()} disabled={!canGenerate} className="btn-primary inline-flex items-center gap-2 rounded-lg">{generateMutation.isPending && <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ivory/40 border-t-ivory" />}{generateMutation.isPending ? "Generating version…" : reports.length ? "Generate new version" : "Generate report"}</button>
              <button type="button" onClick={onOpenOverview} className="btn-secondary inline-flex items-center gap-1.5 rounded-lg"><Icon name="overview" className="h-3.5 w-3.5" />Case Overview</button>
            </div>
          </div>
          {reports.length > 1 && <div className="mt-3 border-t border-line/60 pt-2"><ReportVersionSelector reports={reports} selectedReportId={selectedReport?.report_id ?? null} onSelect={setSelectedReportId} /></div>}
        </header>

        {reportsQuery.isLoading ? <div className="flex h-64 items-center justify-center rounded-lg border border-dashed border-line bg-surface p-6 text-xs text-ink-muted">Loading Case report data…</div> : selectedReport ? <PersistedReportCard key={selectedReport.report_id} report={selectedReport} caseId={caseId} threadTitle={caseTitle} isDownloading={downloadMutation.isPending} onDownloadPdf={() => downloadMutation.mutate(selectedReport)} /> : <NoSavedReport canGenerate={canGenerate} isGenerating={generateMutation.isPending} onGenerate={() => void handleGenerate()} onOpenOverview={analysisResult ? onOpenOverview : onOpenChat} />}
      </div>
      <MeaningfulErrorModal isOpen={Boolean(activeError)} error={activeError} onClose={() => { generateMutation.reset(); downloadMutation.reset(); }} onRetry={handleRetry} />
    </section>
  );
}

function reportRequestKey(): string {
  if (typeof globalThis.crypto?.randomUUID !== "function") throw new Error("The browser does not provide a report idempotency key generator.");
  return globalThis.crypto.randomUUID();
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
