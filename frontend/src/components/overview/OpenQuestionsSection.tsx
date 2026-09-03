import type { CaseGap } from "@/lib/case-overview";

const gapLabels: Record<CaseGap["status"], string> = {
  NOT_PROVIDED: "Not provided", EXPLICITLY_UNKNOWN: "Explicitly unknown",
  AMBIGUOUS: "Ambiguous", CONFLICTING: "Conflicting information",
};

export function OpenQuestionsSection({ gaps, onOpenChat }: {
  gaps: CaseGap[];
  onOpenChat?: () => void;
}) {
  return (
    <section aria-labelledby="overview-open-questions-heading" className="order-4 min-w-0 border-t border-line pt-4 lg:order-2">
      <h2 id="overview-open-questions-heading" className="flex items-baseline gap-2 text-sm font-semibold text-ink">
        Open Questions {gaps.length > 0 && <span className="text-xs font-normal text-ink-muted">{gaps.length}</span>}
      </h2>
      {gaps.length === 0 ? (
        <p className="pt-2 text-xs leading-5 text-ink-secondary">No open questions recorded.</p>
      ) : (
        <div className="divide-y divide-line">
          {gaps.map((gap) => (
            <article key={gap.id} className="space-y-2 py-4 last:pb-1">
              <p className="text-[11px] text-ink-muted">{gapLabels[gap.status]}{gap.askable && " · Needs clarification"}</p>
              <h3 className="text-sm font-semibold leading-6 text-ink">{gap.topic}</h3>
              <p className="text-xs leading-6 text-ink-secondary">{gap.description}</p>
              {gap.reason && <p className="text-xs leading-6 text-ink-secondary"><span className="font-medium">Why it matters: </span>{gap.reason}</p>}
            </article>
          ))}
        </div>
      )}
      {gaps.some((gap) => gap.askable) && onOpenChat && (
        <button type="button" onClick={onOpenChat}
          className="mt-3 min-h-9 text-xs font-semibold underline decoration-line-strong underline-offset-4 hover:decoration-ink focus-visible:ring-2 focus-visible:ring-primary">
          Clarify in Chat <span aria-hidden="true">→</span>
        </button>
      )}
    </section>
  );
}
