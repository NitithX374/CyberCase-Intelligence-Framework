import Link from "next/link";
import { CyberCaseLogo } from "@/components/common/CyberCaseLogo";
import { Icon } from "@/components/common/icons";
import { UserProfileMenu } from "@/components/common/UserProfileMenu";
import type { CaseRead } from "@/lib/api";
import { workspaceViewDescriptions, type RunPhase, type WorkspaceView } from "@/components/common/types";

interface WorkspaceHeaderProps {
  activeCase: CaseRead | null;
  activeCaseId: string | null;
  activeView: WorkspaceView;
  cases: CaseRead[];
  creatingCase: boolean;
  deletingCaseId: string | null;
  phase: RunPhase;
  onViewChange: (view: WorkspaceView) => void;
  onSelectCase: (caseId: string) => void;
  onNewCase: () => void;
  onRequestDelete: (caseRecord: CaseRead) => void;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
}

const phasePresentation: Record<RunPhase, string> = {
  idle: "Ready",
  querying: "Processing",
  awaiting_followup: "Input needed",
  analyzing: "Analyzing",
  ready: "Analysis available",
  error: "Needs attention",
};

const workspaceTabs: Array<{ view: WorkspaceView; label: string }> = [
  { view: "intake", label: "Intake" },
  { view: "overview", label: "Overview" },
  { view: "materials", label: "Materials" },
  { view: "technical-context", label: "Technical" },
  { view: "report", label: "Report" },
];

export function WorkspaceHeader({
  activeCase,
  activeCaseId,
  activeView,
  cases,
  creatingCase,
  deletingCaseId,
  phase,
  onViewChange,
  onSelectCase,
  onNewCase,
  onRequestDelete,
  isChatOpen = true,
  onToggleChat,
}: WorkspaceHeaderProps) {
  const displayCaseTitle = activeCase?.title || "New case";

  return (
    <header className="shrink-0 border-b border-line bg-surface">
      <div className="flex min-h-14 items-center gap-3 px-4 sm:px-5 lg:px-6">
        <Link
          href="/"
          aria-label="CyberCase home"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md focus-visible:ring-2 focus-visible:ring-accent md:hidden"
        >
          <CyberCaseLogo size={30} />
        </Link>

        <div className="min-w-0 flex-1">
          <div className="flex min-w-0 items-center gap-2.5">
            <h1 className="truncate text-[15px] font-semibold tracking-[-0.015em] text-ink sm:text-base">
              {displayCaseTitle}
            </h1>
            <span className="hidden shrink-0 items-center gap-1.5 text-[10px] font-medium text-ink-muted sm:inline-flex">
              <span className={`h-1.5 w-1.5 rounded-full ${phaseDotClass(phase)}`} aria-hidden="true" />
              {phasePresentation[phase]}
            </span>
          </div>
          <p className="mt-0.5 truncate text-[10px] text-ink-muted sm:hidden">{phasePresentation[phase]}</p>
        </div>

        <div className="hidden items-center gap-1.5 md:flex">
          {cases.length > 1 && (
            <select
              value={activeCaseId ?? ""}
              onChange={(event) => event.target.value && onSelectCase(event.target.value)}
              aria-label="Select saved case"
              className="h-8 max-w-52 rounded-md border border-line bg-surface px-2.5 text-[11px] font-medium text-ink outline-none hover:border-line-strong focus-visible:ring-2 focus-visible:ring-accent"
            >
              <option value="">Select case</option>
              {cases.map((caseRecord) => <option key={caseRecord.id} value={caseRecord.id}>{caseRecord.title}</option>)}
            </select>
          )}
          <IconAction label="New case" icon="plus" disabled={creatingCase} onClick={onNewCase} />
          {activeCase && (
            <IconAction
              label={`Delete ${displayCaseTitle}`}
              icon="trash"
              disabled={deletingCaseId !== null}
              onClick={() => onRequestDelete(activeCase)}
            />
          )}
        </div>

        {onToggleChat && (
          <button
            type="button"
            onClick={onToggleChat}
            aria-label={isChatOpen ? "Close Ask" : "Open Ask"}
            title={isChatOpen ? "Close Ask" : "Open Ask"}
            className={`inline-flex h-8 items-center gap-1.5 rounded-md border px-2.5 text-[11px] font-semibold outline-none focus-visible:ring-2 focus-visible:ring-accent ${
              isChatOpen ? "border-accent bg-accent-soft text-accent" : "border-line text-ink hover:bg-surface-hover"
            }`}
          >
            <Icon name="chat" className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Ask</span>
            {phase === "awaiting_followup" && <span className="h-1.5 w-1.5 rounded-full bg-unresolved" aria-hidden="true" />}
          </button>
        )}

        <details className="relative md:hidden">
          <summary aria-label="Open account menu" className="flex h-8 w-8 cursor-pointer list-none items-center justify-center rounded-md text-ink-secondary hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-accent">
            <Icon name="account" className="h-4 w-4" />
          </summary>
          <div className="absolute right-0 top-10 z-50 w-64 border border-line bg-surface p-3 shadow-lg">
            <UserProfileMenu />
          </div>
        </details>
      </div>

      <div className="flex min-h-11 items-center gap-2 border-t border-line/70 px-4 md:hidden">
        {cases.length > 1 && (
          <select
            value={activeCaseId ?? ""}
            onChange={(event) => event.target.value && onSelectCase(event.target.value)}
            aria-label="Select saved case"
            className="h-8 min-w-0 flex-1 rounded-md border border-line bg-surface px-2.5 text-[11px] font-medium text-ink outline-none focus-visible:ring-2 focus-visible:ring-accent"
          >
            <option value="">Select case</option>
            {cases.map((caseRecord) => <option key={caseRecord.id} value={caseRecord.id}>{caseRecord.title}</option>)}
          </select>
        )}
        {cases.length <= 1 && <span className="flex-1 text-[10px] text-ink-muted">Case workspace</span>}
        <IconAction label="New case" icon="plus" disabled={creatingCase} onClick={onNewCase} />
        {activeCase && <IconAction label={`Delete ${displayCaseTitle}`} icon="trash" disabled={deletingCaseId !== null} onClick={() => onRequestDelete(activeCase)} />}
      </div>

      <nav aria-label="Case workspace views" role="tablist" className="flex min-h-10 gap-5 overflow-x-auto px-4 text-[11px] sm:px-5 lg:px-6">
        {workspaceTabs.map((item) => {
          const selected = item.view === activeView;
          return (
            <button
              key={item.view}
              id={`workspace-tab-${item.view}`}
              type="button"
              role="tab"
              aria-selected={selected}
              aria-controls={`workspace-${item.view}-panel`}
              tabIndex={selected ? 0 : -1}
              title={workspaceViewDescriptions[item.view]}
              onClick={() => onViewChange(item.view)}
              className={`shrink-0 border-b-2 px-0.5 pt-1 font-medium outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                selected ? "border-accent text-accent" : "border-transparent text-ink-muted hover:text-ink"
              }`}
            >
              {item.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
}

function IconAction({ label, icon, disabled, onClick }: { label: string; icon: "plus" | "trash"; disabled: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      disabled={disabled}
      onClick={onClick}
      className="flex h-8 w-8 items-center justify-center rounded-md text-ink-secondary hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-wait disabled:opacity-40"
    >
      <Icon name={icon} className="h-3.5 w-3.5" />
    </button>
  );
}

function phaseDotClass(phase: RunPhase): string {
  if (phase === "error") return "bg-critical";
  if (phase === "awaiting_followup") return "bg-unresolved";
  if (phase === "querying" || phase === "analyzing") return "bg-evidence motion-safe:animate-pulse";
  return "bg-established";
}
