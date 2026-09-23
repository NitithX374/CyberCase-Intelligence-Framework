"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { downloadCaseReportHtml, type CaseReport } from "@/lib/api";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { Icon } from "@/components/common/icons";
import { toUserFacingError } from "@/lib/userFacingError";

interface PersistedReportCardProps {
  report: CaseReport;
  caseId: string;
  caseTitle: string;
}

/** A saved report version, as the backend renders it. */
export function PersistedReportCard({ report, caseId, caseTitle }: PersistedReportCardProps) {
  return (
    <article aria-label="Persisted report" className="mt-4">
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
        role="status"
        aria-label="Loading report preview"
        className="flex h-[820px] w-full items-center justify-center rounded-xl bg-surface-nested text-ink-muted"
      >
        <Icon name="spinner" className="h-6 w-6" />
      </div>
    );
  }

  if (error || !htmlUrl) {
    return (
      <>
        <div
          aria-label="Report Preview Unavailable"
          className="flex h-[320px] w-full flex-col items-center justify-center gap-3 rounded-xl bg-surface-nested p-6 text-center"
        >
          <p className="text-sm font-medium text-ink">ไม่สามารถแสดงตัวอย่างรายงานได้</p>
          <button
            type="button"
            onClick={() => {
              setIsModalDismissed(false);
              void refetch();
            }}
            className="btn-secondary h-8 px-3"
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
    <div
      aria-label="HTML Report Viewer"
      className="overflow-hidden rounded-xl border border-line bg-canvas"
    >
      <iframe
        src={htmlUrl}
        title={`Case report: ${title}`}
        className="h-[820px] w-full border-0 bg-canvas"
      />
    </div>
  );
}
