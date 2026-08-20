import type { ReactNode } from "react";
import {
  formatCaseUpdateValue,
  readableValue,
  type CaseUpdateView,
} from "@/lib/case-update";

export function CaseUpdateCard({ update }: { update: CaseUpdateView }) {
  const isUpdated = update.status === "updated" && update.childVersion !== null;
  return (
    <section
      aria-label="Case State update"
      className="mt-5 overflow-hidden rounded-xl border border-[#CAD8CE] bg-[#F1F5F1]"
    >
      <header className="border-b border-[#D8E2DA] px-4 py-3 sm:px-5">
        <p className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-[#516257]">
          {isUpdated ? "Case updated" : "Case State unchanged"}
        </p>
        <p className="mt-1 text-sm font-extrabold text-ink">
          {isUpdated
            ? `Case State V${update.parentVersion} → V${update.childVersion}`
            : `Case State V${update.parentVersion} · No new version`}
        </p>
      </header>

      <div className="grid gap-px bg-[#D8E2DA] md:grid-cols-3">
        <UpdateColumn title="Added">
          {update.added.length > 0 ? (
            <ul className="space-y-2">
              {update.added.map((item) => (
                <li key={`${item.targetType}:${item.targetId}`}>
                  <p className="text-[10px] font-bold uppercase tracking-[0.08em] text-[#66736A]">
                    {readableValue(item.targetType)}
                  </p>
                  <p className="mt-0.5 text-xs leading-5 text-ink">{item.summary}</p>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyColumn text="No ADD operations." />
          )}
        </UpdateColumn>

        <UpdateColumn title="Changed">
          {update.changed.length > 0 ? (
            <ul className="space-y-3">
              {update.changed.map((item) => (
                <li key={`${item.targetType}:${item.targetId}:${item.field}`}>
                  <p className="text-xs font-bold text-ink">
                    {item.targetId} · {readableValue(item.field)}
                  </p>
                  <p className="mt-1 text-[11px] leading-5 text-ink-secondary">
                    {formatCaseUpdateValue(item.oldValue)} → {formatCaseUpdateValue(item.newValue)}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyColumn text="No MODIFY operations." />
          )}
        </UpdateColumn>

        <UpdateColumn title="Current unresolved information">
          {update.currentUnresolvedInformation === null ? (
            <EmptyColumn text="No validated Gap Analysis is available." />
          ) : update.currentUnresolvedInformation.length === 0 ? (
            <EmptyColumn text="No unresolved items were returned." />
          ) : (
            <ul className="space-y-3">
              {update.currentUnresolvedInformation.map((gap, index) => (
                <li key={`${gap.topic}:${gap.status}:${index}`}>
                  <div className="flex flex-wrap items-center gap-1.5">
                    <p className="text-xs font-bold text-ink">{gap.topic}</p>
                    <span className="rounded-full border border-[#C8D2CA] px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-[0.06em] text-[#66736A]">
                      {gap.priority}
                    </span>
                  </div>
                  <p className="mt-1 text-[11px] leading-5 text-ink-secondary">
                    {gap.description}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </UpdateColumn>
      </div>
      <p className="border-t border-[#D8E2DA] px-4 py-2.5 text-[10px] leading-4 text-[#66736A] sm:px-5">
        Derived deterministically from the committed Case State delta. This card
        does not infer gap resolution or removal.
      </p>
    </section>
  );
}

function UpdateColumn({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="min-w-0 bg-[#F7F9F7] px-4 py-4">
      <h3 className="text-[10px] font-extrabold uppercase tracking-[0.12em] text-[#516257]">
        {title}
      </h3>
      <div className="mt-3">{children}</div>
    </div>
  );
}

function EmptyColumn({ text }: { text: string }) {
  return <p className="text-[11px] leading-5 text-ink-secondary">{text}</p>;
}
