import { Icon } from "@/components/common/icons";

interface CaseOverviewHeaderProps {
  threadTitle: string;
  onOpenReport: () => void;
  onOpenMaterials?: () => void;
}

export function CaseOverviewHeader({ threadTitle, onOpenReport, onOpenMaterials }: CaseOverviewHeaderProps) {
  return (
    <header aria-label={`${threadTitle} analysis`} className="flex flex-wrap items-start justify-between gap-4 border-b border-line pb-5">
      <div>
        <h2 className="text-xl font-semibold tracking-[-0.02em] text-ink sm:text-2xl">Analysis</h2>
        <p className="mt-1.5 max-w-2xl text-xs leading-5 text-ink-muted">
          Grounded findings from the persisted Case Analysis Result and its evidence snapshot.
        </p>
      </div>
      <div className="flex items-center gap-3">
        {onOpenMaterials && (
          <button type="button" onClick={onOpenMaterials} className="text-xs font-medium text-ink-secondary underline decoration-line-strong underline-offset-4 hover:text-ink focus-visible:ring-2 focus-visible:ring-accent">
            View sources
          </button>
        )}
        <button type="button" onClick={onOpenReport} className="inline-flex h-9 items-center gap-1.5 rounded-md bg-primary px-3.5 text-xs font-semibold text-ivory hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2">
          <Icon name="report" className="h-3.5 w-3.5" />
          View report
        </button>
      </div>
    </header>
  );
}
