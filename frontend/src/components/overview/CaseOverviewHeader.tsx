import { Icon } from "@/components/common/icons";

interface CaseOverviewHeaderProps {
  threadTitle: string;
  onOpenChat: () => void;
  onOpenReport: () => void;
  onOpenMaterials?: () => void;
}

export function CaseOverviewHeader({
  threadTitle,
  onOpenChat,
  onOpenReport,
  onOpenMaterials,
}: CaseOverviewHeaderProps) {
  return (
    <header className="border-b border-line pb-5">
      <h1 className="max-w-3xl break-words text-2xl font-extrabold tracking-[-0.035em] text-ink sm:text-3xl">
        {threadTitle}
      </h1>
      <div className="mt-5 flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={onOpenChat}
          className="btn-secondary inline-flex items-center gap-1.5 rounded-lg"
        >
          <Icon name="chat" className="h-3.5 w-3.5" />
          Ask about this case
        </button>
        {onOpenMaterials && (
          <button
            type="button"
            onClick={onOpenMaterials}
            className="btn-secondary inline-flex items-center gap-1.5 rounded-lg"
          >
            <Icon name="materials" className="h-3.5 w-3.5" />
            View sources
          </button>
        )}
        <button
          type="button"
          onClick={onOpenReport}
          className="btn-primary inline-flex items-center gap-1.5 rounded-lg"
        >
          <Icon name="report" className="h-3.5 w-3.5" />
          View Report
        </button>
      </div>
    </header>
  );
}
