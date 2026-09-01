interface ReportEmptyStateProps {
  onReturn: () => void;
}

export function ReportEmptyState({ onReturn }: ReportEmptyStateProps) {
  return (
    <section
      id="workspace-report-panel"
      role="tabpanel"
      aria-label="Case report"
      className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-canvas p-6 sm:p-10"
    >
      <div className="workspace-card mx-auto max-w-lg space-y-3 p-8 text-center">
        <p className="section-eyebrow">CASE REPORT</p>
        <h2 className="text-lg font-extrabold tracking-tight text-ink">Select a Case</h2>
        <p className="text-xs text-ink-secondary">
          Open or create an investigation case before generating a report.
        </p>
        <div className="pt-2">
          <button
            type="button"
            onClick={onReturn}
            className="btn-primary inline-flex items-center gap-2 rounded-lg"
          >
            Return to Case
          </button>
        </div>
      </div>
    </section>
  );
}
