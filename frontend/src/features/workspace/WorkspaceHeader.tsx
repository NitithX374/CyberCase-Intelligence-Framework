"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { Icon, type IconName } from "@/components/icons";
import { AccountMenu } from "@/features/auth/AccountMenu";
import { formatDate } from "@/lib/format";
import type { CaseRead } from "@/lib/api/types";
import { casePath, type WorkspaceView } from "@/lib/casePaths";

interface WorkspaceHeaderProps {
  activeCase: CaseRead | null;
  activeView: WorkspaceView;
  creatingCase: boolean;
  status: string;
  statusNeedsAttention: boolean;
  analyzeLabel: string;
  canAnalyze: boolean;
  findingCount?: number;
  flaggedCount?: number;
  sourceCount?: number;
  analysedAt?: string | null;
  onAnalyze?: () => void;
  onViewChange: (view: WorkspaceView) => void;
  onNewCase: () => void;
  onRenameCase?: (title: string) => void;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
  waitingQuestions?: number;
}

const viewLabels: Record<WorkspaceView, string> = {
  analysis: "Findings",
  legal: "Findings",
  sources: "Sources",
  report: "Report",
};

const sectionLabels: Record<string, string> = {
  timeline: "Timeline",
  people: "People",
  impact: "Impact",
  technical: "ATT&CK techniques",
  legal: "Related laws",
};

const compactTabs: Array<{ view: WorkspaceView; label: string; icon: IconName }> = [
  { view: "analysis", label: "Findings", icon: "findings" },
  { view: "sources", label: "Sources", icon: "sources" },
  { view: "report", label: "Report", icon: "report" },
];

export function WorkspaceHeader({
  activeCase,
  activeView,
  creatingCase,
  status,
  statusNeedsAttention,
  analyzeLabel,
  canAnalyze,
  findingCount = 0,
  flaggedCount = 0,
  sourceCount,
  analysedAt,
  onAnalyze,
  onViewChange,
  onNewCase,
  onRenameCase,
  isChatOpen = true,
  onToggleChat,
  waitingQuestions = 0,
}: WorkspaceHeaderProps) {
  const [renaming, setRenaming] = useState(false);
  const displayCaseTitle = activeCase?.title || "New case";
  const currentView: WorkspaceView = activeView === "legal" ? "analysis" : activeView;
  const caseId = activeCase?.id;
  const section = usePathname()?.match(/\/analysis\/([^/?#]+)/)?.[1];

  const titleRow = (onBand: boolean) => (
    <div className="flex min-w-0 items-center gap-2">
      {renaming ? (
        <CaseTitleField
          title={displayCaseTitle}
          onCommit={(next) => {
            setRenaming(false);
            if (next && next !== displayCaseTitle) onRenameCase?.(next);
          }}
        />
      ) : (
        <>
          <h1
            className={`min-w-0 truncate font-bold tracking-[-0.01em] ${
              onBand ? "text-2xl sm:text-3xl" : "text-2xl text-ink"
            }`}
            title={displayCaseTitle}
          >
            {displayCaseTitle}
          </h1>
          {onRenameCase && activeCase && (
            <button
              type="button"
              onClick={() => setRenaming(true)}
              aria-label="Rename case"
              title="Rename case"
              className={`inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg transition-colors ${
                onBand
                  ? "text-white hover:bg-white/10 focus-visible:outline-white"
                  : "text-ink-muted hover:bg-surface-hover hover:text-primary"
              }`}
            >
              <Icon name="edit" className="text-lg" />
            </button>
          )}
        </>
      )}
    </div>
  );

  return (
    <header className="flex shrink-0 flex-col gap-5 px-3 pt-4 sm:px-6 lg:px-8 lg:pt-5">
      <div className="flex min-h-12 items-center gap-3 border-b border-line-strong pb-4">
        <Link href="/case" className="hidden text-sm font-semibold text-ink sm:inline lg:hidden">
          CyberCase
        </Link>
        <nav
          aria-label="Case workspace views"
          className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto lg:hidden"
        >
          {compactTabs.map((item) => {
            const selected = item.view === currentView;
            return (
              <button
                key={item.view}
                id={`workspace-tab-${item.view}`}
                type="button"
                aria-current={selected ? "page" : undefined}
                onClick={() => onViewChange(item.view)}
                className={`inline-flex min-h-10 shrink-0 items-center gap-1.5 rounded-lg px-3 text-sm ${
                  selected ? "bg-primary-soft font-semibold text-primary" : "text-ink-secondary"
                }`}
              >
                <Icon name={item.icon} className="hidden text-lg sm:inline-flex" />
                {item.label}
              </button>
            );
          })}
        </nav>
        <p className="hidden min-w-0 flex-1 truncate text-sm text-ink-muted lg:block">
          <Link href="/case" className="font-medium text-primary hover:underline">
            All cases
          </Link>
          <span aria-hidden="true" className="px-2">
            ›
          </span>
          {displayCaseTitle}
          <span aria-hidden="true" className="px-2">
            ›
          </span>
          {(currentView === "analysis" && sectionLabels[section ?? ""]) || viewLabels[activeView]}
        </p>
        {onToggleChat && (
          <button
            id="ask-toggle"
            type="button"
            onClick={onToggleChat}
            aria-label={
              isChatOpen
                ? "Close Ask"
                : waitingQuestions > 0
                  ? `Open Ask, ${waitingQuestions} question waiting`
                  : "Open Ask"
            }
            aria-pressed={isChatOpen}
            aria-controls="workspace-chat-panel"
            className={`inline-flex h-10 shrink-0 items-center gap-2 rounded-lg px-3.5 text-sm font-semibold transition-[background-color,border-color,transform] active:scale-[0.98] ${
              isChatOpen
                ? "border border-line-strong bg-surface text-ink hover:bg-surface-hover"
                : "bg-espresso text-white hover:bg-espresso-raised"
            }`}
          >
            <Icon name="chat" className="text-xl" />
            <span className="hidden sm:inline">
              {isChatOpen
                ? "Close Ask"
                : waitingQuestions > 0
                  ? "Question waiting"
                  : "Ask about this case"}
            </span>
            {!isChatOpen && waitingQuestions > 0 && (
              <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-md bg-primary px-1.5 text-xs font-bold text-white tabular-nums">
                {waitingQuestions}
              </span>
            )}
          </button>
        )}
        <AccountMenu
          actions={[
            { label: "All cases", icon: "folder", href: "/case" },
            { label: "New case", icon: "plus", onSelect: onNewCase, disabled: creatingCase },
          ]}
        />
      </div>

      {currentView !== "analysis" ? (
        <div className="sheet flex flex-wrap items-center gap-x-4 gap-y-3 px-5 py-4 sm:px-6">
          <div className="min-w-0 flex-1">{titleRow(false)}</div>
          <span role="status" className={statusNeedsAttention ? "badge-check" : "badge-linked"}>
            {status}
          </span>
          {onAnalyze && (
            <button
              type="button"
              onClick={onAnalyze}
              disabled={!canAnalyze}
              className="btn-primary"
            >
              <Icon name={analyzeLabel === "Analyzing…" ? "spinner" : "play"} className="text-lg" />
              {analyzeLabel}
            </button>
          )}
        </div>
      ) : (
        <div className="relative overflow-hidden rounded-xl bg-primary px-5 py-6 text-white sm:px-8 sm:py-7">
          <div className="relative flex flex-wrap items-center gap-6">
            <div className="min-w-0 flex-1 basis-full sm:basis-0">
              {titleRow(true)}
              <p className="mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-white">
                {sourceCount !== undefined && (
                  <span className="hidden sm:inline">
                    {sourceCount} {sourceCount === 1 ? "source" : "sources"} ·
                  </span>
                )}
                {analysedAt && (
                  <span className="hidden sm:inline">
                    Analyzed {formatDate(analysedAt, "dayTime")} ·
                  </span>
                )}
                <span
                  role="status"
                  className={
                    statusNeedsAttention
                      ? "rounded-md bg-white px-2 py-0.5 font-semibold text-primary"
                      : undefined
                  }
                >
                  {status}
                </span>
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                {onAnalyze && (
                  <button
                    type="button"
                    onClick={onAnalyze}
                    disabled={!canAnalyze}
                    className="btn-on-band"
                  >
                    <Icon
                      name={analyzeLabel === "Analyzing…" ? "spinner" : "play"}
                      className="text-lg"
                    />
                    {analyzeLabel}
                  </button>
                )}
                {caseId && (
                  <Link href={casePath(caseId, "report")} className="btn-band-line">
                    <Icon name="report" className="text-lg" />
                    Create report
                  </Link>
                )}
              </div>
            </div>
            {findingCount > 0 && (
              <div className="hidden flex-col items-center gap-2 sm:flex">
                <FlagRing flagged={flaggedCount} total={findingCount} />
                <span className="text-xs text-white">Findings to check against the source</span>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

function CaseTitleField({ title, onCommit }: { title: string; onCommit: (next: string) => void }) {
  const field = useRef<HTMLInputElement | null>(null);
  const [value, setValue] = useState(title);

  useEffect(() => {
    field.current?.focus();
    field.current?.select();
  }, []);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onCommit(value.trim());
  };

  return (
    <form onSubmit={submit} className="min-w-0 flex-1">
      <label className="sr-only" htmlFor="case-title-field">
        Case title
      </label>
      <input
        id="case-title-field"
        ref={field}
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onBlur={() => onCommit(value.trim())}
        onKeyDown={(event) => {
          if (event.key === "Escape") onCommit("");
        }}
        maxLength={200}
        className="h-11 w-full min-w-0 rounded-lg border border-line-strong bg-white px-3 text-xl font-semibold text-ink outline-none focus:border-primary"
      />
    </form>
  );
}

const RING_RADIUS = 50;
const RING_LENGTH = 2 * Math.PI * RING_RADIUS;

function FlagRing({ flagged, total }: { flagged: number; total: number }) {
  const offset = RING_LENGTH * (1 - (total ? flagged / total : 0));
  return (
    <div className="relative flex h-28 w-28 items-center justify-center">
      <svg viewBox="0 0 112 112" aria-hidden="true" className="absolute inset-0 -rotate-90">
        <circle
          cx="56"
          cy="56"
          r={RING_RADIUS}
          fill="none"
          stroke="rgba(255,255,255,0.22)"
          strokeWidth="6"
        />
        <circle
          key={`${flagged}/${total}`}
          cx="56"
          cy="56"
          r={RING_RADIUS}
          fill="none"
          stroke="#ffffff"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={RING_LENGTH}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="relative flex flex-col items-center leading-tight">
        <span className="text-2xl font-bold tabular-nums">
          <span>{flagged}</span>/{total}
        </span>
        <span className="text-xs text-white">to check</span>
      </div>
    </div>
  );
}
