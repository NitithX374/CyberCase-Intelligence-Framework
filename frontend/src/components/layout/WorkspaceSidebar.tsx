"use client";

import { useState } from "react";
import Link from "next/link";
import { CyberCaseLogo } from "@/components/common/CyberCaseLogo";
import type { CaseRead } from "@/lib/api";
import { Icon, type IconName } from "@/components/common/icons";
import type { WorkspaceView } from "@/components/common/types";
import { UserProfileMenu } from "@/components/common/UserProfileMenu";

interface WorkspaceNavigationProps {
  cases: CaseRead[];
  activeCaseId: string | null;
  casesLoading: boolean;
  casesError: string | null;
  onSelectCase: (caseId: string) => void;
  onNewCase: () => void;
  onRequestDelete: (caseRecord: CaseRead) => void;
  deletingCaseId: string | null;
  activeView: WorkspaceView;
  onViewChange: (view: WorkspaceView) => void;
}

const railDestinations: Array<{ view: WorkspaceView; label: string; icon: IconName }> = [
  { view: "overview", label: "Case analysis", icon: "overview" },
  { view: "materials", label: "Case materials", icon: "materials" },
  { view: "technical-context", label: "Technical context", icon: "technical" },
  { view: "report", label: "Case report", icon: "report" },
];

export function WorkspaceSidebar(props: WorkspaceNavigationProps) {
  const [isCaseDrawerOpen, setIsCaseDrawerOpen] = useState(false);

  const createCase = () => {
    props.onNewCase();
    setIsCaseDrawerOpen(false);
  };

  const selectCase = (caseId: string) => {
    props.onSelectCase(caseId);
    setIsCaseDrawerOpen(false);
  };

  return (
    <aside className="relative z-40 hidden h-full w-14 shrink-0 flex-col border-r border-line bg-sidebar md:flex">
      <Link
        href="/"
        aria-label="CyberCase home"
        title="CyberCase home"
        className="flex h-14 items-center justify-center border-b border-line outline-none hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-accent"
      >
        <CyberCaseLogo size={28} />
      </Link>

      <nav aria-label="Workspace shortcuts" className="flex flex-1 flex-col items-center gap-1.5 py-3">
        <RailButton label="New case" icon="plus" onClick={createCase} />
        <RailButton
          label="Cases"
          icon="materials"
          selected={isCaseDrawerOpen}
          expanded={isCaseDrawerOpen}
          controls="workspace-case-drawer"
          onClick={() => setIsCaseDrawerOpen((open) => !open)}
        />
        <span className="my-1 h-px w-7 bg-line" aria-hidden="true" />
        {railDestinations.map((item) => (
          <RailButton
            key={item.view}
            label={item.label}
            icon={item.icon}
            selected={!isCaseDrawerOpen && props.activeView === item.view}
            onClick={() => {
              props.onViewChange(item.view);
              setIsCaseDrawerOpen(false);
            }}
          />
        ))}
      </nav>

      <RailButton
        label="Account and cases"
        icon="account"
        selected={isCaseDrawerOpen}
        onClick={() => setIsCaseDrawerOpen(true)}
        className="mb-3"
      />

      <WorkspaceCaseDrawer
        isOpen={isCaseDrawerOpen}
        cases={props.cases}
        activeCaseId={props.activeCaseId}
        casesLoading={props.casesLoading}
        casesError={props.casesError}
        deletingCaseId={props.deletingCaseId}
        onClose={() => setIsCaseDrawerOpen(false)}
        onSelectCase={selectCase}
        onNewCase={createCase}
        onRequestDelete={props.onRequestDelete}
      />
    </aside>
  );
}

function RailButton({
  label,
  icon,
  selected = false,
  expanded,
  controls,
  className = "",
  onClick,
}: {
  label: string;
  icon: IconName;
  selected?: boolean;
  expanded?: boolean;
  controls?: string;
  className?: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      aria-expanded={expanded}
      aria-controls={controls}
      onClick={onClick}
      className={`mx-auto flex h-10 w-10 items-center justify-center rounded-md outline-none transition-colors focus-visible:ring-2 focus-visible:ring-accent ${
        selected ? "bg-accent-soft text-accent" : "text-ink-secondary hover:bg-surface-hover hover:text-ink"
      } ${className}`}
    >
      <Icon name={icon} className="h-[18px] w-[18px]" />
    </button>
  );
}

const caseStatusLabels: Record<CaseRead["status"], string> = {
  idle: "Ready",
  processing: "Analyzing",
  awaiting_followup: "Input needed",
  answered: "Analysis available",
  failed: "Needs attention",
};

function WorkspaceCaseDrawer({
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
}: {
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
}) {
  if (!isOpen) return null;

  return (
    <section id="workspace-case-drawer" aria-label="Saved cases" className="absolute inset-y-0 left-full flex w-72 flex-col border-r border-line bg-surface shadow-[6px_0_18px_rgba(31,42,36,0.08)]">
      <header className="flex h-14 items-center justify-between border-b border-line px-4">
        <h2 className="text-sm font-semibold text-ink">Cases</h2>
        <button type="button" onClick={onClose} aria-label="Close cases" className="flex h-8 w-8 items-center justify-center rounded-md text-ink-muted hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-accent"><Icon name="close" className="h-4 w-4" /></button>
      </header>

      <div className="border-b border-line p-3">
        <button type="button" onClick={onNewCase} className="flex h-9 w-full items-center justify-center gap-2 rounded-md bg-primary px-3 text-xs font-semibold text-ivory hover:bg-charcoal-hover focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"><Icon name="plus" className="h-3.5 w-3.5" />New case</button>
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
                  <button type="button" aria-current={selected ? "page" : undefined} aria-label={`${caseRecord.title}, ${caseStatusLabels[caseRecord.status]}`} onClick={() => onSelectCase(caseRecord.id)} className={`min-w-0 flex-1 rounded-md px-2.5 py-2 text-left outline-none focus-visible:ring-2 focus-visible:ring-accent ${selected ? "bg-accent-soft text-ink" : "text-ink-secondary hover:bg-surface-hover hover:text-ink"}`}>
                    <span className="block truncate text-xs font-semibold">{caseRecord.title}</span>
                    <span className="mt-1 block text-[10px] text-ink-muted">{caseStatusLabels[caseRecord.status]}</span>
                  </button>
                  <button type="button" aria-label={`Delete ${caseRecord.title}`} title={`Delete ${caseRecord.title}`} disabled={deletingCaseId !== null} onClick={() => onRequestDelete(caseRecord)} className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-ink-muted opacity-0 hover:bg-danger/10 hover:text-danger focus:opacity-100 focus-visible:ring-2 focus-visible:ring-danger group-hover:opacity-100"><Icon name="trash" className="h-3.5 w-3.5" /></button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <div className="border-t border-line p-3"><UserProfileMenu /></div>
    </section>
  );
}
