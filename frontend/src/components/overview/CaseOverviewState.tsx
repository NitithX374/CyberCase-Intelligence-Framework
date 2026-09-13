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
    <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-6 text-center sm:p-10">
      <div className="workspace-card max-w-md space-y-3 p-8">
        {processing ? (
          <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-xl bg-evidence/10 text-evidence">
            <span className="h-2.5 w-2.5 rounded-full bg-evidence motion-safe:animate-ping motion-reduce:animate-none" />
          </div>
        ) : eyebrow ? (
          <p className="section-eyebrow">{eyebrow}</p>
        ) : null}
        <h2 className="text-base font-extrabold tracking-tight text-ink sm:text-lg">
          {title}
        </h2>
        <p className="text-xs leading-relaxed text-ink-secondary">{description}</p>
        <div className="pt-3">
          <button
            type="button"
            onClick={onAction}
            className="btn-primary inline-flex items-center gap-2 rounded-lg"
          >
            {actionIcon && <Icon name={actionIcon} className="h-3.5 w-3.5" />}
            {actionLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
