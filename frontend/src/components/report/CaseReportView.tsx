"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useRef, useState } from "react";
import {
  downloadCaseReportPdf,
  generateCaseReport,
  listCaseReports,
  type CaseAnalysisResultRead,
  type CaseRunRead,
  type CaseReport,
} from "@/lib/api";
import { caseQueryKeys } from "@/hooks/useCaseQueries";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError, type UserFacingError } from "@/lib/user-facing-error";
import { PersistedReportCard } from "./PersistedReportCard";
import { Icon } from "@/components/common/icons";

interface CaseReportViewProps {
  caseId: string;
  caseTitle: string;
  analysisResult: CaseAnalysisResultRead | null;
  runStatus: CaseRunRead["status"] | null;
  onOpenOverview: () => void;
}

export function CaseReportView({ caseId, caseTitle, analysisResult, runStatus, onOpenOverview }: CaseReportViewProps) {
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
      queryClient.setQueryData<CaseReport[]>(caseQueryKeys.reports(caseId), (current) => [report, ...(current ?? []).filter((item) => item.report_id !== report.report_id)]);
      setSelectedReportId(report.report_id);
    },
  });
  const downloadMutation = useMutation({
    mutationFn: (report: CaseReport) => downloadCaseReportPdf(caseId, report.report_id),
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
    <section id="workspace-report-panel" role="tabpanel" aria-label="Case report" className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-surface">
      <div className="mx-auto w-full max-w-5xl space-y-8 px-5 py-7 sm:px-8 sm:py-9 lg:px-10">
        <header className="border-b border-line pb-5">
          <div className="flex flex-wrap items-baseline justify-between gap-4">
            <div>
              <h2 className="text-xl font-semibold tracking-[-0.02em] text-ink sm:text-2xl">Report</h2>
              <p className="mt-1.5 max-w-2xl text-xs leading-5 text-ink-muted">Each saved version remains bound to its Case Analysis Result and Case evidence revision.</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button type="button" onClick={onOpenOverview} className="inline-flex h-9 items-center gap-1.5 px-2 text-xs font-medium text-ink-secondary underline decoration-line-strong underline-offset-4"><Icon name="overview" className="h-3.5 w-3.5" />View analysis</button>
              <button type="button" onClick={() => void handleGenerate()} disabled={!canGenerate} className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-3.5 text-xs font-semibold text-ivory hover:bg-charcoal-hover disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled">{generateMutation.isPending && <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ivory/40 border-t-ivory" />}{generateMutation.isPending ? "Generating…" : reports.length ? "New version" : "Generate report"}</button>
            </div>
          </div>
          {reports.length > 1 && <div className="mt-3 border-t border-line/60 pt-2"><ReportVersionSelector reports={reports} selectedReportId={selectedReport?.report_id ?? null} onSelect={setSelectedReportId} /></div>}
        </header>

        {reportsQuery.isLoading ? <div className="flex h-64 items-center justify-center border-y border-line p-6 text-xs text-ink-muted">Loading Case report data…</div> : selectedReport ? <PersistedReportCard key={selectedReport.report_id} report={selectedReport} caseId={caseId} caseTitle={caseTitle} isDownloading={downloadMutation.isPending} onDownloadPdf={() => downloadMutation.mutate(selectedReport)} /> : <NoSavedReport canGenerate={canGenerate} isGenerating={generateMutation.isPending} onGenerate={() => void handleGenerate()} onOpenOverview={onOpenOverview} />}
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

function ReportVersionSelector({
  reports,
  selectedReportId,
  onSelect,
}: {
  reports: CaseReport[];
  selectedReportId: string | null;
  onSelect: (reportId: string) => void;
}) {
  if (reports.length <= 1) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5" aria-label="Report version history">
      <span className="mr-1 text-[10px] font-medium text-ink-muted">Versions</span>
      {reports.map((report) => {
        const isSelected = report.report_id === selectedReportId;
        return (
          <button
            key={report.report_id}
            type="button"
            onClick={() => onSelect(report.report_id)}
            className={`border-b-2 px-1 py-1 text-xs font-semibold transition-colors ${isSelected ? "border-accent text-accent" : "border-transparent text-ink-muted hover:border-line-strong hover:text-ink"}`}
          >
            <span>v{report.version_number}</span>
            {report.persistence_status === "failed" && <span className="ml-1 text-[9px] font-normal text-red-400">(failed)</span>}
          </button>
        );
      })}
    </div>
  );
}

function NoSavedReport({
  canGenerate,
  isGenerating,
  onGenerate,
  onOpenOverview,
}: {
  canGenerate: boolean;
  isGenerating: boolean;
  onGenerate: () => void;
  onOpenOverview?: () => void;
}) {
  return (
    <div className="mx-auto my-8 max-w-2xl border-y border-line py-8 text-center">
      <Icon name="report" className="mx-auto h-5 w-5 text-ink-muted" />
      <div>
        <h2 className="mt-3 text-base font-semibold tracking-tight text-ink sm:text-lg">
          {canGenerate ? "No Saved Report for This Case" : "Case material required · ยังไม่มีข้อมูลสำนวนคดี"}
        </h2>
        <p className="mx-auto mt-1 max-w-xl text-xs leading-relaxed text-ink-secondary">
          {canGenerate
            ? "A preliminary case analysis report can be compiled from submitted case material and optional external technical context when applicable."
            : "กรุณากรอกรายละเอียดสำนวนคดีในหน้า Case Materials เพื่อให้ระบบประมวลผลก่อนสร้างรายงานวิเคราะห์คดี"}
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-3 pt-5">
        {canGenerate ? (
          <button type="button" onClick={onGenerate} disabled={isGenerating} className="btn-primary inline-flex min-h-9 items-center gap-2 rounded-md">
            {isGenerating ? <><span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ivory/30 border-t-ivory" /><span>Generating report...</span></> : <span>Generate report</span>}
          </button>
        ) : (
          <button type="button" onClick={onOpenOverview} className="btn-primary inline-flex min-h-9 items-center gap-2 rounded-md">
            <Icon name="materials" className="h-3.5 w-3.5" />
            <span>Go to Case Materials · เปิดสำนวนคดี</span>
          </button>
        )}
      </div>
    </div>
  );
}
