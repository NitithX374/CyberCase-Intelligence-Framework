"use client";

import type { CaseRead } from "@/lib/api";
import { Icon } from "@/components/common/icons";
import { UserProfileMenu } from "@/components/common/UserProfileMenu";

interface WorkspaceCaseDrawerProps {
  isOpen: boolean;
  cases: CaseRead[];
  activeCaseId: string | null;
  casesLoading: boolean;
  casesError: string | null;
  deletingCaseId: string | null;
  onClose: () => void;
  onSelectCase: (caseId: string) => void;
  onNewCase: () => void;
  onRequestDelete: (caseRecord: CaseRead) => void;
}

const caseStatusLabels: Record<CaseRead["status"], string> = {
  idle: "Ready",
  processing: "Analyzing",
  awaiting_followup: "Input needed",
  answered: "Analysis available",
  failed: "Needs attention",
};

export function WorkspaceCaseDrawer({
  isOpen,
  cases,
  activeCaseId,
  casesLoading,
  casesError,
  deletingCaseId,
  onClose,
  onSelectCase,
  onNewCase,
  onRequestDelete,
}: WorkspaceCaseDrawerProps) {
  if (!isOpen) return null;

  return (
    <section
      id="workspace-case-drawer"
      aria-label="Saved cases"
      className="absolute inset-y-0 left-full flex w-72 flex-col border-r border-line bg-surface shadow-[6px_0_18px_rgba(31,42,36,0.08)]"
    >
      <header className="flex h-14 items-center justify-between border-b border-line px-4">
        <h2 className="text-sm font-semibold text-ink">Cases</h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close cases"
          className="flex h-8 w-8 items-center justify-center rounded-md text-ink-muted hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-accent"
        >
          <Icon name="close" className="h-4 w-4" />
        </button>
      </header>

      <div className="border-b border-line p-3">
        <button
          type="button"
          onClick={onNewCase}
          className="flex h-9 w-full items-center justify-center gap-2 rounded-md bg-primary px-3 text-xs font-semibold text-ivory hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        >
          <Icon name="plus" className="h-3.5 w-3.5" />
          New case
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-3">
        {casesLoading ? (
          <p className="px-1 py-3 text-xs text-ink-muted" role="status">Loading cases…</p>
        ) : casesError ? (
          <p className="px-1 py-3 text-xs leading-5 text-critical">Cases could not be loaded.</p>
        ) : cases.length === 0 ? (
          <p className="px-1 py-3 text-xs leading-5 text-ink-muted">No saved cases yet.</p>
        ) : (
          <ul className="divide-y divide-line">
            {cases.map((caseRecord) => {
              const selected = caseRecord.id === activeCaseId;
              return (
                <li key={caseRecord.id} className="group flex items-center gap-1 py-1.5">
                  <button
                    type="button"
                    aria-current={selected ? "page" : undefined}
                    aria-label={`${caseRecord.title}, ${caseStatusLabels[caseRecord.status]}`}
                    onClick={() => onSelectCase(caseRecord.id)}
                    className={`min-w-0 flex-1 rounded-md px-2.5 py-2 text-left outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                      selected ? "bg-accent-soft text-ink" : "text-ink-secondary hover:bg-surface-hover hover:text-ink"
                    }`}
                  >
                    <span className="block truncate text-xs font-semibold">{caseRecord.title}</span>
                    <span className="mt-1 block text-[10px] text-ink-muted">{caseStatusLabels[caseRecord.status]}</span>
                  </button>
                  <button
                    type="button"
                    aria-label={`Delete ${caseRecord.title}`}
                    title={`Delete ${caseRecord.title}`}
                    disabled={deletingCaseId !== null}
                    onClick={() => onRequestDelete(caseRecord)}
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-ink-muted opacity-0 hover:bg-danger/10 hover:text-danger focus:opacity-100 focus-visible:ring-2 focus-visible:ring-danger group-hover:opacity-100"
                  >
                    <Icon name="trash" className="h-3.5 w-3.5" />
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <div className="border-t border-line p-3">
        <UserProfileMenu />
      </div>
    </section>
  );
}
