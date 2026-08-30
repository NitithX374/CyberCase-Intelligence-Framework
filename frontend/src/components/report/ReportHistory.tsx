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
    <div className="space-y-4 border border-dashed border-line rounded-lg bg-surface p-6 sm:p-8 text-center max-w-2xl mx-auto my-8">
      <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-surface-nested text-ink">
        <Icon name="report" className="h-5 w-5" />
      </div>
      <div>
        <h2 className="text-base font-bold text-ink sm:text-lg">
          {canGenerate
            ? "No Saved Report for This Case"
            : "Case Intake Required · ยังไม่มีข้อมูลสำนวนคดี"}
        </h2>
        <p className="mt-1 text-xs leading-relaxed text-ink-secondary">
          {canGenerate
            ? "A preliminary case analysis report can be compiled from user-reported evidence and validated MITRE ATT&CK threat intelligence."
            : "กรุณากรอกรายละเอียดสำนวนคดีในหน้า Case Intake เพื่อให้ระบบประมวลผลก่อนสร้างรายงานวิเคราะห์คดี"}
        </p>
      </div>

      <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
        {canGenerate ? (
          <button
            type="button"
            onClick={onGenerate}
            disabled={isGenerating}
            className="inline-flex min-h-9 items-center gap-2 rounded bg-primary px-4 py-2 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
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
            className="inline-flex min-h-9 items-center gap-2 rounded bg-primary px-4 py-2 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary"
          >
            <Icon name="intake" className="h-3.5 w-3.5" />
            <span>Go to Case Intake · เปิดสำนวนคดี</span>
          </button>
        )}
      </div>
    </div>
  );
}
