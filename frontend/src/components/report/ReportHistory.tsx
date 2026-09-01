import type { ChatReportRead } from "@/lib/api";
import { Icon } from "@/components/common/icons";

interface ReportVersionSelectorProps {
  reports: ChatReportRead[];
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
      <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-ink-muted mr-1">
        Versions:
      </span>
      {reports.map((report) => {
        const isSelected = report.report_id === selectedReportId;
        return (
          <button
            key={report.report_id}
            type="button"
            onClick={() => onSelect(report.report_id)}
            className={`rounded px-2.5 py-1 text-xs font-bold transition-colors ${
              isSelected
                ? "bg-primary text-ivory shadow-xs"
                : "border border-line bg-surface text-ink hover:border-ink hover:bg-surface-hover"
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
    <div className="workspace-card mx-auto my-8 max-w-2xl space-y-4 p-6 text-center sm:p-8">
      <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-surface-nested text-ink-secondary">
        <Icon name="report" className="h-5 w-5" />
      </div>
      <div>
        <h2 className="text-base font-extrabold tracking-tight text-ink sm:text-lg">
          {canGenerate
            ? "No Saved Report for This Case"
            : "Case Intake Required · ยังไม่มีข้อมูลสำนวนคดี"}
        </h2>
        <p className="mt-1 text-xs leading-relaxed text-ink-secondary">
          {canGenerate
            ? "A preliminary case analysis report can be compiled from submitted case material and optional external technical context when applicable."
            : "กรุณากรอกรายละเอียดสำนวนคดีในหน้า Case Intake เพื่อให้ระบบประมวลผลก่อนสร้างรายงานวิเคราะห์คดี"}
        </p>
      </div>

      <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
        {canGenerate ? (
          <button
            type="button"
            onClick={onGenerate}
            disabled={isGenerating}
            className="btn-primary inline-flex min-h-9 items-center gap-2 rounded-lg"
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
            className="btn-primary inline-flex min-h-9 items-center gap-2 rounded-lg"
          >
            <Icon name="intake" className="h-3.5 w-3.5" />
            <span>Go to Case Intake · เปิดสำนวนคดี</span>
          </button>
        )}
      </div>
    </div>
  );
}
