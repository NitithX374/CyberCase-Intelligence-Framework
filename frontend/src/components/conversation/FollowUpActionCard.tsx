import type { ChatFollowUpGapDetail } from "@/lib/chat-followup";
import { StatusPill } from "@/components/common/StatusPill";
import { Icon } from "@/components/common/icons";

export function FollowUpActionCard({
  detail,
}: {
  detail: ChatFollowUpGapDetail;
}) {
  return (
    <aside className="mt-4 overflow-hidden rounded-2xl border border-unresolved/30 bg-unresolved/5">
      <div className="border-l-4 border-unresolved px-4 py-3.5 sm:px-5">
        <div className="flex flex-wrap items-center gap-2">
          <StatusPill tone="attention">Needs clarification</StatusPill>
          <span className="text-[11px] font-medium text-ink-secondary">
            Your answer can improve the current analysis.
          </span>
        </div>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-ink-muted">
              What remains unclear
            </p>
            <p className="mt-1 text-xs leading-relaxed text-ink">
              <strong className="font-bold">{detail.topic}</strong>
              <span>:</span> {detail.description}
            </p>
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.1em] text-ink-muted">
              Why this matters
            </p>
            <p className="mt-1 text-xs leading-relaxed text-ink-secondary">{detail.reason}</p>
          </div>
        </div>
      </div>
      <details className="group border-t border-unresolved/20 px-4 py-2.5 sm:px-5">
        <summary className="flex cursor-pointer list-none items-center justify-between gap-2 text-[11px] font-bold text-ink outline-none marker:hidden focus-visible:ring-2 focus-visible:ring-primary">
          <span>Why is CyberCase asking this?</span>
          <Icon
            name="chevron"
            className="h-3.5 w-3.5 text-ink-muted transition-transform duration-150 group-open:rotate-180"
          />
        </summary>
        <p className="pt-2 text-[11px] leading-relaxed text-ink-secondary">{detail.affects}</p>
      </details>
    </aside>
  );
}
