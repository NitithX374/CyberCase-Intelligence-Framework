import {
  formatCaseUpdateValue,
  readableValue,
  type CaseUpdateView,
} from "@/lib/case-update";

interface CaseStateDeltaViewProps {
  update: CaseUpdateView;
  isUpdated: boolean;
}

export function CaseStateDeltaView({
  update,
  isUpdated,
}: CaseStateDeltaViewProps) {
  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-[#CAD8CE] bg-[#F1F5F1] p-4">
        <p className="text-[10px] font-extrabold uppercase tracking-[0.16em] text-[#516257]">
          {isUpdated ? "Case updated" : "Case State unchanged"}
        </p>
        <p className="mt-1 text-sm font-extrabold text-ink">
          {isUpdated
            ? `Case State V${update.parentVersion} → V${update.childVersion}`
            : `Case State V${update.parentVersion} · No new version`}
        </p>
      </div>

      <section aria-label="Added operations" className="space-y-2.5">
        <h3 className="text-xs font-extrabold uppercase tracking-wide text-ink">
          Added ({update.added.length})
        </h3>
        {update.added.length > 0 ? (
          <ul className="space-y-2">
            {update.added.map((item) => (
              <li
                key={`${item.targetType}:${item.targetId}`}
                className="rounded-xl border border-line bg-surface p-3 shadow-2xs"
              >
                <div className="flex items-center gap-2">
                  <span className="rounded bg-[#E2EAE4] px-1.5 py-0.5 text-[9.5px] font-extrabold uppercase tracking-wide text-[#3E5244]">
                    {readableValue(item.targetType)}
                  </span>
                  <span className="font-mono text-[10px] font-bold text-ink-muted">
                    {item.targetId}
                  </span>
                </div>
                <p className="mt-1.5 text-xs leading-relaxed text-ink">
                  {item.summary}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-xl border border-line bg-surface/50 p-3 text-xs text-ink-muted">
            No ADD operations in this version.
          </p>
        )}
      </section>

      <section aria-label="Changed operations" className="space-y-2.5">
        <h3 className="text-xs font-extrabold uppercase tracking-wide text-ink">
          Changed ({update.changed.length})
        </h3>
        {update.changed.length > 0 ? (
          <ul className="space-y-2">
            {update.changed.map((item) => (
              <li
                key={`${item.targetType}:${item.targetId}:${item.field}`}
                className="rounded-xl border border-line bg-surface p-3 shadow-2xs"
              >
                <p className="text-xs font-bold text-ink">
                  {item.targetId} · {readableValue(item.field)}
                </p>
                <div className="mt-1.5 flex items-center gap-1.5 text-xs text-ink-secondary">
                  <span className="rounded bg-surface-hover px-1.5 py-0.5 font-mono text-[11px]">
                    {formatCaseUpdateValue(item.oldValue)}
                  </span>
                  <span>→</span>
                  <span className="rounded bg-[#E2EAE4] px-1.5 py-0.5 font-mono text-[11px] font-bold text-[#3E5244]">
                    {formatCaseUpdateValue(item.newValue)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-xl border border-line bg-surface/50 p-3 text-xs text-ink-muted">
            No MODIFY operations in this version.
          </p>
        )}
      </section>

      <p className="text-[10.5px] leading-relaxed text-ink-muted">
        Derived deterministically from the committed Case State delta.
      </p>
    </div>
  );
}
