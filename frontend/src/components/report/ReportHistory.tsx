import type { ChatReportRead } from "@/lib/api";
import { Icon } from "@/components/common/icons";

interface ReportVersionHistoryProps {
  reports: ChatReportRead[];
  selectedReportId: string | null;
  onSelect: (reportId: string) => void;
}

export function ReportVersionHistory({
  reports,
  selectedReportId,
  onSelect,
}: ReportVersionHistoryProps) {
  return (
    <aside aria-label="Report version history" className="space-y-3">
      <p className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-ink-secondary">
        Report versions
      </p>
      <div className="mt-3 space-y-2" aria-label="Saved report versions">
        {reports.map((report) => {
          const isSelected = report.report_id === selectedReportId;
          return (
            <button
              key={report.report_id}
              type="button"
              onClick={() => onSelect(report.report_id)}
              className={`w-full rounded-xl border px-3 py-3 text-left outline-none transition-colors focus-visible:ring-2 focus-visible:ring-primary ${
                isSelected
                  ? "border-primary bg-primary text-ivory"
                  : "border-line bg-surface text-ink hover:border-primary hover:bg-surface-hover"
              }`}
            >
              <span className="block text-sm font-extrabold">
                Version {report.version_number}
              </span>
              <span
                className={`mt-1 block text-[10px] font-bold uppercase tracking-[0.1em] ${
                  isSelected ? "text-ivory/70" : "text-ink-secondary"
                }`}
              >
                {report.persistence_status === "completed"
                  ? "Validated output"
                  : "Generation failed"}
              </span>
            </button>
          );
        })}
      </div>
    </aside>
  );
}

export function NoSavedReport() {
  return (
    <div className="mt-8 max-w-3xl rounded-2xl border border-dashed border-line-strong bg-surface p-6 sm:p-8">
      <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary text-ivory shadow-sm">
        <Icon name="report" className="h-6 w-6" />
      </span>
      <h2 className="mt-5 text-xl font-extrabold tracking-tight text-ink">
        No saved report for this chat
      </h2>
      <p className="mt-3 text-sm leading-6 text-ink-secondary">
        Complete the chat and wait for a grounded analysis, then
        generate a report. Previous report attempts will remain available here
        as versioned history.
      </p>
    </div>
  );
}
