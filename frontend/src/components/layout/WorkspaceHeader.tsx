import Link from "next/link";
import type { ChatThreadRead } from "@/lib/api";
import { Icon } from "@/components/common/icons";
import {
  workspaceViewLabels,
  type RunPhase,
  type WorkspaceView,
} from "@/components/common/types";

interface WorkspaceHeaderProps {
  activeThread: ChatThreadRead | null;
  activeThreadId: string | null;
  activeView: WorkspaceView;
  threads: ChatThreadRead[];
  creatingThread: boolean;
  deletingThreadId: string | null;
  phase: RunPhase;
  onViewChange: (view: WorkspaceView) => void;
  onSelectThread: (threadId: string) => void;
  onNewChat: () => void;
  onRequestDelete: (thread: ChatThreadRead) => void;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
}

const phasePresentation: Record<RunPhase, { label: string }> = {
  idle: { label: "Ready" },
  querying: { label: "Processing" },
  awaiting_followup: { label: "Your input is needed" },
  analyzing: { label: "Validating" },
  ready: { label: "Complete" },
  error: { label: "Error" },
};

export function WorkspaceHeader({
  activeThread,
  activeThreadId,
  activeView,
  threads,
  creatingThread,
  deletingThreadId,
  phase,
  onViewChange,
  onSelectThread,
  onNewChat,
  onRequestDelete,
  isChatOpen = true,
  onToggleChat,
}: WorkspaceHeaderProps) {
  const displayThreadTitle =
    activeThread?.title === "New chat" || !activeThread?.title
      ? "New case"
      : activeThread.title;
  const currentPhase = phasePresentation[phase];

  return (
    <header className="shrink-0 border-b border-line bg-surface px-4 py-3 sm:px-6 md:px-8 md:py-3.5">
      <div className="flex min-w-0 items-center gap-3">
        <Link
          href="/"
          aria-label="CyberCase home"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary text-sm font-extrabold text-ivory outline-none transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 md:hidden"
        >
          C
        </Link>
        <div className="min-w-0 flex-1">
          <div className="hidden items-center gap-2 text-[9px] font-bold uppercase tracking-[0.16em] text-ink-muted sm:flex">
            <span>Case file</span>
            <span aria-hidden="true">/</span>
            <span>{workspaceViewLabels[activeView]}</span>
          </div>
          <p className="truncate text-sm font-extrabold tracking-[-0.02em] text-ink sm:mt-0.5 sm:text-base">
            {displayThreadTitle}
          </p>
          {activeView !== "intake" && (
            <div className="mt-1 flex items-center gap-2 text-[10px] font-medium text-ink-secondary">
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  phase === "error"
                    ? "bg-critical"
                    : phase === "querying" || phase === "analyzing"
                      ? "bg-evidence motion-safe:animate-pulse motion-reduce:animate-none"
                      : phase === "awaiting_followup"
                        ? "bg-unresolved"
                        : "bg-established"
                }`}
                aria-hidden="true"
              />
              <span>{currentPhase.label}</span>
            </div>
          )}
        </div>

        {onToggleChat && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onToggleChat}
              aria-label={isChatOpen ? "Close AI Copilot" : "Open AI Copilot"}
              title={isChatOpen ? "Close Copilot" : "Open Copilot"}
              className={`inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-bold transition-all focus-visible:ring-2 focus-visible:ring-primary ${
                isChatOpen
                  ? "border-primary bg-primary text-ivory shadow-xs"
                  : "border-line bg-canvas text-ink hover:border-line-strong hover:bg-surface-hover"
              }`}
            >
              <Icon name="chat" className="h-4 w-4" />
              <span className="hidden sm:inline">Copilot</span>
              {phase === "awaiting_followup" && (
                <span
                  className="h-2 w-2 rounded-full bg-unresolved motion-safe:animate-ping"
                  aria-hidden="true"
                />
              )}
            </button>
          </div>
        )}
      </div>

      <div className="mt-3 grid gap-2 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto] md:hidden">
        <label className="sr-only" htmlFor="mobile-workspace-view">
          Select workspace
        </label>
        <select
          id="mobile-workspace-view"
          value={activeView}
          onChange={(event) => onViewChange(event.target.value as WorkspaceView)}
          aria-label="Select workspace"
          className="min-h-10 min-w-0 rounded-lg border border-line bg-canvas px-3 text-xs font-bold text-ink outline-none hover:border-line-strong focus-visible:ring-2 focus-visible:ring-primary"
        >
          <option value="intake">Intake</option>
          <option value="overview">Overview</option>
          <option value="materials">Case Materials</option>
          <option value="technical-context">Technical Context</option>
          <option value="report">Report</option>
        </select>
        <label className="sr-only" htmlFor="mobile-saved-case">
          Select saved case
        </label>
        <select
          id="mobile-saved-case"
          value={activeThreadId ?? ""}
          onChange={(event) => {
            if (event.target.value) onSelectThread(event.target.value);
          }}
          aria-label="Select saved case"
          className="min-h-10 min-w-0 rounded-lg border border-line bg-canvas px-3 text-xs font-bold text-ink outline-none hover:border-line-strong focus-visible:ring-2 focus-visible:ring-primary"
        >
          <option value="">Select case</option>
          {threads.map((thread) => (
            <option key={thread.id} value={thread.id}>
              {thread.title === "New chat" ? "New case" : thread.title}
            </option>
          ))}
        </select>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={onNewChat}
            disabled={creatingThread}
            aria-label="New case"
            title="New case"
            className="flex min-h-10 min-w-10 flex-1 items-center justify-center rounded-lg border border-line bg-canvas text-ink outline-none transition-colors hover:border-line-strong hover:bg-surface-hover active:bg-surface-nested focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
          >
            <Icon name="plus" className="h-4 w-4" />
          </button>
          {activeThread && (
            <button
              type="button"
              onClick={() => onRequestDelete(activeThread)}
              disabled={deletingThreadId !== null}
              aria-label={`Delete ${displayThreadTitle}`}
              title={`Delete ${displayThreadTitle}`}
              className="flex min-h-10 min-w-10 flex-1 items-center justify-center rounded-lg border border-line bg-canvas text-ink-secondary outline-none transition-colors hover:border-accent hover:bg-accent-soft hover:text-accent focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
            >
              <Icon name="trash" className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
