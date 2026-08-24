"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import {
  downloadChatReportPdf,
  type ChatReportRead,
} from "@/lib/api";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/user-facing-error";

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
      className="space-y-4"
    >
      <header className="flex flex-wrap items-baseline justify-between gap-3 border-b border-line pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] font-bold tracking-wider text-ink-muted uppercase">
              Version {report.version_number} · Saved
            </span>
            <span className="text-[10px] font-semibold text-ink-muted">
              {report.persistence_status === "completed"
                ? "Provisional"
                : "Generation failed"}
            </span>
          </div>
          <h2 className="mt-1 text-lg font-bold tracking-tight text-ink sm:text-xl">
            {report.report?.title ?? threadTitle}
          </h2>
        </div>

        {report.persistence_status === "completed" && report.report && (
          <button
            type="button"
            onClick={onDownloadPdf}
            disabled={isDownloading}
            className="inline-flex items-center gap-1.5 rounded bg-primary px-3.5 py-1.5 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
          >
            {isDownloading ? "Preparing PDF..." : "Download PDF"}
          </button>
        )}
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
  const [isModalDismissed, setIsModalDismissed] = useState(false);

  const {
    data: pdfBlob,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["report-pdf-blob", threadId, reportId],
    queryFn: () => downloadChatReportPdf(threadId, reportId),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  const pdfUrl = useMemo(() => {
    if (
      !pdfBlob ||
      typeof window === "undefined" ||
      typeof window.URL?.createObjectURL !== "function"
    ) {
      return null;
    }
    return window.URL.createObjectURL(pdfBlob);
  }, [pdfBlob]);

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

  const pdfUserFacingError = useMemo(() => {
    if (!error) return null;
    return toUserFacingError(error, { actionLabel: "โหลดตัวอย่าง PDF ใหม่" });
  }, [error]);

  if (isLoading) {
    return (
      <div
        aria-label="Loading PDF preview"
        className="flex h-[750px] w-full flex-col items-center justify-center rounded-lg border border-dashed border-line bg-surface p-6 text-center text-ink-secondary"
      >
        <div
          className="h-6 w-6 animate-spin rounded-full border-2 border-primary/30 border-t-primary"
          aria-hidden="true"
        />
        <p className="mt-3 text-xs font-bold text-ink">Loading PDF report...</p>
        <p className="mt-0.5 text-[11px] text-ink-muted">
          Retrieving formatted case analysis document.
        </p>
      </div>
    );
  }

  if (error || !pdfUrl) {
    return (
      <>
        <div
          aria-label="PDF Preview Unavailable"
          className="flex h-[400px] w-full flex-col items-center justify-center rounded-lg border border-dashed border-line bg-surface p-6 text-center space-y-3"
        >
          <p className="text-xs font-semibold text-ink">ไม่สามารถแสดงตัวอย่าง PDF ได้</p>
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
          isOpen={!isModalDismissed && Boolean(pdfUserFacingError)}
          error={pdfUserFacingError}
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
    <div
      aria-label="PDF Document Viewer"
      className="overflow-hidden rounded-lg border border-line bg-surface shadow-xs"
    >
      <iframe
        src={`${pdfUrl}#toolbar=1&navpanes=0`}
        title={`PDF Report: ${title}`}
        className="h-[800px] w-full border-0 bg-canvas sm:h-[850px]"
      />
    </div>
  );
}

function ReportFailure({ report }: { report: ChatReportRead }) {
  return (
    <div className="rounded-lg border border-line bg-surface p-5 text-xs space-y-3">
      <div className="flex items-center gap-2 text-accent">
        <span className="font-bold text-sm">ไม่สามารถจัดทำรายงานฉบับนี้ได้</span>
      </div>
      <p className="text-ink-secondary leading-relaxed">
        {report.failure_message ?? "ระบบไม่สามารถสร้างรายงานฉบับสมบูรณ์ได้เนื่องจากข้อมูลบางส่วนไม่ผ่านเกณฑ์การตรวจสอบ"}
      </p>
      <p className="text-ink-muted text-[11px]">
        คุณสามารถเริ่มวิเคราะห์ข้อมูลเพิ่มเติมในหน้า Chat หรือสร้างรายงานฉบับใหม่เมื่อปรับปรุงข้อมูลเรียบร้อยแล้ว
      </p>
      {(report.failure_code || report.validation_errors.length > 0) && (
        <details className="mt-3 rounded border border-line/60 bg-surface-nested/30 px-3 py-2 text-xs">
          <summary className="cursor-pointer font-medium text-ink-muted transition-colors hover:text-ink select-none flex items-center justify-between">
            <span>Technical details</span>
            <span className="text-[10px] transition-transform duration-200 group-open:rotate-180">
              ▾
            </span>
          </summary>
          <div className="mt-2 pt-2 border-t border-line/40 font-mono text-[11px] text-ink-secondary break-all select-text whitespace-pre-wrap space-y-1">
            {report.failure_code && (
              <div>
                <span className="text-ink-muted">Failure code: </span>
                <span>{report.failure_code}</span>
              </div>
            )}
            {report.validation_errors.length > 0 && (
              <div>
                <div className="text-ink-muted">Validation errors:</div>
                <ul className="list-disc pl-4 mt-1 space-y-0.5">
                  {report.validation_errors.map((err, i) => (
                    <li key={`validation-error-${i}`}>{err}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </details>
      )}
    </div>
  );
}
