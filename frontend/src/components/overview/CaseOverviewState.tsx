import { Icon } from "@/components/common/icons";

interface CaseOverviewStateProps {
  eyebrow?: string;
  title: string;
  description: string;
  actionLabel: string;
  onAction: () => void;
  actionIcon?: "chat" | "intake";
  processing?: boolean;
}

export function CaseOverviewState({
  eyebrow,
  title,
  description,
  actionLabel,
  onAction,
  actionIcon,
  processing,
}: CaseOverviewStateProps) {
  return (
    <div className="mx-auto flex h-full min-h-[360px] w-full max-w-5xl flex-col justify-center px-5 py-10 sm:px-8 lg:px-10">
      <div className="max-w-xl border-y border-line py-8">
        {processing ? (
          <div className="mb-4 flex items-center gap-2 text-evidence">
            <span className="h-2 w-2 rounded-full bg-evidence motion-safe:animate-pulse motion-reduce:animate-none" />
            <span className="text-[11px] font-semibold">Analysis in progress</span>
          </div>
        ) : eyebrow ? (
          <p className="section-eyebrow">{eyebrow}</p>
        ) : null}
        <h2 className="text-lg font-semibold tracking-tight text-ink sm:text-xl">
          {title}
        </h2>
        <p className="mt-2 max-w-lg text-xs leading-6 text-ink-secondary">{description}</p>
        <div className="pt-5">
          <button
            type="button"
            onClick={onAction}
            className="btn-primary inline-flex items-center gap-2 rounded-md"
          >
            {actionIcon && <Icon name={actionIcon} className="h-3.5 w-3.5" />}
            {actionLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
