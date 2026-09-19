"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { downloadCaseReportHtml, type CaseReport } from "@/lib/api";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/userFacingError";

interface PersistedReportCardProps {
  report: CaseReport;
  caseId: string;
  caseTitle: string;
  isDownloading: boolean;
  onDownloadPdf: () => void;
}

export function PersistedReportCard({
  report,
  caseId,
  caseTitle,
  isDownloading,
  onDownloadPdf,
}: PersistedReportCardProps) {
  return (
    <article aria-label="Persisted report" className="space-y-4">
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-line pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] font-semibold tracking-wider text-ink-muted">
              Version {report.version_number} · Saved
            </span>
            <span className="text-[10px] font-semibold text-ink-muted">Provisional</span>
          </div>
          <h2 className="mt-1 text-lg font-bold tracking-tight text-ink sm:text-xl">
            {report.report.title ?? caseTitle}
          </h2>
        </div>

        <button
          type="button"
          onClick={onDownloadPdf}
          disabled={isDownloading}
          className="inline-flex items-center gap-1.5 rounded bg-primary px-3.5 py-1.5 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
        >
          {isDownloading ? "Preparing PDF..." : "Download PDF"}
        </button>
      </header>

      <ReportHtmlViewer
        caseId={caseId}
        reportId={report.report_id}
        title={report.report.title ?? caseTitle}
      />
    </article>
  );
}

function ReportHtmlViewer({
  caseId,
  reportId,
  title,
}: {
  caseId: string;
  reportId: string;
  title: string;
}) {
  const [isModalDismissed, setIsModalDismissed] = useState(false);

  const {
    data: htmlBlob,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["case-report-html-blob", caseId, reportId],
    queryFn: () => downloadCaseReportHtml(caseId, reportId),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  const htmlUrl = useMemo(() => {
    if (
      !htmlBlob ||
      typeof window === "undefined" ||
      typeof window.URL?.createObjectURL !== "function"
    ) {
      return null;
    }
    return window.URL.createObjectURL(htmlBlob);
  }, [htmlBlob]);

  useEffect(() => {
    return () => {
      if (
        htmlUrl &&
        typeof window !== "undefined" &&
        typeof window.URL?.revokeObjectURL === "function"
      ) {
        window.URL.revokeObjectURL(htmlUrl);
      }
    };
  }, [htmlUrl]);

  const htmlUserFacingError = useMemo(() => {
    if (!error) return null;
    return toUserFacingError(error, { actionLabel: "โหลดตัวอย่างรายงานใหม่" });
  }, [error]);

  if (isLoading) {
    return (
      <div
        aria-label="Loading report preview"
        className="flex h-[750px] w-full flex-col items-center justify-center border-y border-line bg-surface p-6 text-center text-ink-secondary"
      >
        <div
          className="h-6 w-6 animate-spin rounded-full border-2 border-primary/30 border-t-primary"
          aria-hidden="true"
        />
        <p className="mt-3 text-xs font-bold text-ink">Loading report...</p>
        <p className="mt-0.5 text-[11px] text-ink-muted">
          Retrieving formatted case analysis document.
        </p>
      </div>
    );
  }

  if (error || !htmlUrl) {
    return (
      <>
        <div
          aria-label="Report Preview Unavailable"
          className="flex h-[400px] w-full flex-col items-center justify-center space-y-3 border-y border-line bg-surface p-6 text-center"
        >
          <p className="text-xs font-semibold text-ink">ไม่สามารถแสดงตัวอย่างรายงานได้</p>
          <p className="text-[11px] text-ink-secondary">
            กรุณาลองโหลดเอกสารใหม่อีกครั้ง หรือดาวน์โหลดไฟล์ PDF โดยตรง
          </p>
          <button
            type="button"
            onClick={() => {
              setIsModalDismissed(false);
              void refetch();
            }}
            className="inline-flex items-center gap-1.5 rounded border border-line bg-surface px-3 py-1.5 text-xs font-bold text-ink transition-colors hover:border-ink hover:bg-surface-hover"
          >
            ลองโหลดใหม่
          </button>
        </div>
        <MeaningfulErrorModal
          isOpen={!isModalDismissed && Boolean(htmlUserFacingError)}
          error={htmlUserFacingError}
          onClose={() => setIsModalDismissed(true)}
          onRetry={() => {
            setIsModalDismissed(false);
            void refetch();
          }}
        />
      </>
    );
  }

  return (
    <div aria-label="HTML Report Viewer" className="overflow-hidden border border-line bg-surface">
      <iframe
        src={htmlUrl}
        title={`Case report: ${title}`}
        className="h-[800px] w-full border-0 bg-canvas sm:h-[850px]"
      />
    </div>
  );
}
