import type { CaseGap } from "@/lib/case-overview";
import { StatusPill, type StatusPillTone } from "@/components/common/StatusPill";
import { WorkspaceSectionHeader } from "@/components/common/WorkspaceSectionHeader";
import { Icon } from "@/components/common/icons";

interface OpenQuestionsSectionProps {
  gaps: CaseGap[];
  onOpenChat?: () => void;
}

export function OpenQuestionsSection({
  gaps,
  onOpenChat,
}: OpenQuestionsSectionProps) {
  return (
    <section
      aria-labelledby="overview-open-questions-heading"
      className="workspace-card p-4 sm:p-5"
    >
      <WorkspaceSectionHeader
        eyebrow="03 / NEEDS ATTENTION"
        headingId="overview-open-questions-heading"
        title={
          <>
            Open Questions
            <span className="ml-2 text-sm font-normal text-ink-secondary">
              · ประเด็นที่ยังต้องตรวจสอบ
            </span>
          </>
        }
        description="Only material gaps are shown here. Minor recognition or spelling issues do not become warning states."
        aside={
          <span className="rounded-full border border-line bg-surface px-2.5 py-1 text-[10px] font-bold text-ink-secondary">
            {gaps.length}
          </span>
        }
      />

      {gaps.length === 0 ? (
        <div className="flex items-start gap-2.5 pt-4">
          <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-established/10 text-established">
            <Icon name="overview" className="h-3 w-3" />
          </span>
          <p className="text-xs leading-relaxed text-ink-secondary">
            No structured information gaps were recorded for this analysis.
          </p>
        </div>
      ) : (
        <div className="space-y-3 pt-4">
          {gaps.map((gap) => (
            <GapCard key={gap.id} gap={gap} onOpenChat={onOpenChat} />
          ))}
        </div>
      )}
    </section>
  );
}

function GapCard({
  gap,
  onOpenChat,
}: {
  gap: CaseGap;
  onOpenChat?: () => void;
}) {
  const presentation = gapPresentation(gap);

  return (
    <article className="rounded-xl border border-line bg-canvas/55 p-3.5">
      <StatusPill tone={presentation.tone}>{presentation.label}</StatusPill>
      <h3 className="mt-2 text-sm font-bold leading-snug text-ink">{gap.topic}</h3>
      <p className="mt-1.5 text-xs leading-relaxed text-ink-secondary">{gap.description}</p>

      {gap.reason && (
        <details className="group mt-3 border-t border-line/70 pt-2.5">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-2 text-[11px] font-bold text-ink outline-none marker:hidden focus-visible:ring-2 focus-visible:ring-primary">
            <span>Why this matters</span>
            <Icon
              name="chevron"
              className="h-3 w-3 text-ink-muted transition-transform duration-150 group-open:rotate-180"
            />
          </summary>
          <p className="pt-2 text-[11px] leading-relaxed text-ink-secondary">{gap.reason}</p>
        </details>
      )}

      {gap.askable && onOpenChat && (
        <button
          type="button"
          onClick={onOpenChat}
          className="mt-3 inline-flex items-center gap-1.5 text-[11px] font-bold text-ink transition-colors hover:text-accent hover:underline focus-visible:ring-2 focus-visible:ring-primary"
        >
          Clarify in Chat
          <span aria-hidden="true">→</span>
        </button>
      )}
    </article>
  );
}

function gapPresentation(gap: CaseGap): {
  label: string;
  tone: StatusPillTone;
} {
  if (gap.askable) return { label: "Needs clarification", tone: "attention" };
  if (gap.status === "CONFLICTING") {
    return { label: "Conflicting evidence", tone: "attention" };
  }
  if (gap.status === "EXPLICITLY_UNKNOWN") {
    return { label: "Known limitation", tone: "neutral" };
  }
  return { label: "Needs verification", tone: "neutral" };
}
