import type { CaseReport } from "@/lib/api";
import { Icon } from "@/components/common/icons";

interface ReportVersionSelectorProps {
  reports: CaseReport[];
  selectedReportId: string | null;
  onSelect: (reportId: string) => void;
}

export function ReportVersionSelector({
  reports,
  selectedReportId,
  onSelect,
}: ReportVersionSelectorProps) {
  if (reports.length <= 1) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5" aria-label="Report version history">
      <span className="mr-1 text-[10px] font-medium text-ink-muted">
        Versions
      </span>
      {reports.map((report) => {
        const isSelected = report.report_id === selectedReportId;
        return (
          <button
            key={report.report_id}
            type="button"
            onClick={() => onSelect(report.report_id)}
            className={`border-b-2 px-1 py-1 text-xs font-semibold transition-colors ${
              isSelected
                ? "border-accent text-accent"
                : "border-transparent text-ink-muted hover:border-line-strong hover:text-ink"
            }`}
          >
            <span>v{report.version_number}</span>
            {report.persistence_status === "failed" && (
              <span className="ml-1 text-[9px] text-red-400 font-normal">(failed)</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

export function NoSavedReport({
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
          {canGenerate
            ? "No Saved Report for This Case"
            : "Case Intake Required · ยังไม่มีข้อมูลสำนวนคดี"}
        </h2>
        <p className="mx-auto mt-1 max-w-xl text-xs leading-relaxed text-ink-secondary">
          {canGenerate
            ? "A preliminary case analysis report can be compiled from submitted case material and optional external technical context when applicable."
            : "กรุณากรอกรายละเอียดสำนวนคดีในหน้า Case Intake เพื่อให้ระบบประมวลผลก่อนสร้างรายงานวิเคราะห์คดี"}
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-3 pt-5">
        {canGenerate ? (
          <button
            type="button"
            onClick={onGenerate}
            disabled={isGenerating}
            className="btn-primary inline-flex min-h-9 items-center gap-2 rounded-md"
          >
            {isGenerating ? (
              <>
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-ivory/30 border-t-ivory" />
                <span>Generating report...</span>
              </>
            ) : (
              <span>Generate report</span>
            )}
          </button>
        ) : (
          <button
            type="button"
            onClick={onOpenOverview}
            className="btn-primary inline-flex min-h-9 items-center gap-2 rounded-md"
          >
            <Icon name="intake" className="h-3.5 w-3.5" />
            <span>Go to Case Intake · เปิดสำนวนคดี</span>
          </button>
        )}
      </div>
    </div>
  );
}
