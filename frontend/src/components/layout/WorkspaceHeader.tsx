"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { CyberCaseLogo } from "@/components/common/CyberCaseLogo";
import { Icon } from "@/components/common/icons";
import { UserProfileMenu } from "@/components/common/UserProfileMenu";
import type { CaseRead } from "@/lib/api";
import { workspaceViewDescriptions, type WorkspaceView } from "@/components/common/types";

interface WorkspaceHeaderProps {
  activeCase: CaseRead | null;
  activeView: WorkspaceView;
  creatingCase: boolean;
  hasAnalysis: boolean;
  canAnalyze: boolean;
  isAnalyzing: boolean;
  isStale: boolean;
  onAnalyze: () => void;
  onViewChange: (view: WorkspaceView) => void;
  onNewCase: () => void;
  onRenameCase?: (title: string) => void;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
}

/** What the case is doing, in the two states the workspace can be in. */
function caseStatus(hasAnalysis: boolean, isAnalyzing: boolean, isStale: boolean) {
  if (isAnalyzing) return { label: "Analysing", dot: "bg-accent motion-safe:animate-pulse" };
  if (isStale) return { label: "Analysis is out of date", dot: "bg-unresolved" };
  if (hasAnalysis) return { label: "Analysis available", dot: "bg-established" };
  return { label: "Ready", dot: "bg-line-strong" };
}

const workspaceTabs: Array<{ view: WorkspaceView; label: string }> = [
  { view: "sources", label: "Sources" },
  { view: "analysis", label: "Analysis" },
];

export function WorkspaceHeader({
  activeCase,
  activeView,
  creatingCase,
  hasAnalysis,
  canAnalyze,
  isAnalyzing,
  isStale,
  onAnalyze,
  onViewChange,
  onNewCase,
  onRenameCase,
  isChatOpen = true,
  onToggleChat,
}: WorkspaceHeaderProps) {
  const status = caseStatus(hasAnalysis, isAnalyzing, isStale);
  const [renaming, setRenaming] = useState(false);
  const displayCaseTitle = activeCase?.title || "New case";

  return (
    <header className="shrink-0 border-b border-line bg-surface">
      <div className="flex min-h-14 items-center gap-3 px-4 sm:px-5 lg:px-6">
        <Link
          href="/case"
          aria-label="All cases"
          title="All cases"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md outline-none hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-accent"
        >
          <CyberCaseLogo size={28} />
        </Link>

        <div className="min-w-0 flex-1">
          <div className="flex min-w-0 items-center gap-2.5">
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
                <h1 className="truncate text-[15px] font-semibold tracking-[-0.015em] text-ink sm:text-base">
                  {displayCaseTitle}
                </h1>
                {onRenameCase && activeCase && (
                  <button
                    type="button"
                    onClick={() => setRenaming(true)}
                    aria-label="Rename case"
                    title="Rename case"
                    className="flex h-6 w-6 shrink-0 items-center justify-center rounded text-ink-muted outline-none hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-accent"
                  >
                    <Icon name="edit" className="h-3.5 w-3.5" />
                  </button>
                )}
              </>
            )}
            <span className="hidden shrink-0 items-center gap-1.5 text-[10px] font-medium text-ink-muted sm:inline-flex">
              <span className={`h-1.5 w-1.5 rounded-full ${status.dot}`} aria-hidden="true" />
              {status.label}
            </span>
          </div>
          <p className="mt-0.5 truncate text-[10px] text-ink-muted sm:hidden">{status.label}</p>
        </div>

        <button
          type="button"
          onClick={onAnalyze}
          disabled={!canAnalyze || isAnalyzing}
          title={canAnalyze ? undefined : "Add a case source before analysing"}
          className={`inline-flex h-8 shrink-0 items-center gap-1.5 rounded-md px-3 text-[11px] font-semibold outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled ${
            isStale
              ? "bg-unresolved text-ivory hover:brightness-110"
              : "bg-primary text-ivory hover:bg-charcoal-hover"
          }`}
        >
          {isAnalyzing ? "Analyzing…" : isStale ? "Analyze latest" : "Analyze"}
        </button>

        <Link
          href="/case"
          aria-label="All cases"
          title="All cases"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-ink-secondary outline-none hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-accent"
        >
          <Icon name="list" className="h-3.5 w-3.5" />
        </Link>

        <button
          type="button"
          aria-label="New case"
          title="New case"
          disabled={creatingCase}
          onClick={onNewCase}
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-ink-secondary hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-wait disabled:opacity-40"
        >
          <Icon name="plus" className="h-3.5 w-3.5" />
        </button>

        {onToggleChat && (
          <button
            type="button"
            onClick={onToggleChat}
            aria-label={isChatOpen ? "Close Ask" : "Open Ask"}
            title={isChatOpen ? "Close Ask" : "Open Ask"}
            className={`inline-flex h-8 shrink-0 items-center gap-1.5 rounded-md border px-2.5 text-[11px] font-semibold outline-none focus-visible:ring-2 focus-visible:ring-accent ${
              isChatOpen
                ? "border-accent bg-accent-soft text-accent"
                : "border-line text-ink hover:bg-surface-hover"
            }`}
          >
            <Icon name="chat" className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Ask</span>
          </button>
        )}

        <details className="relative shrink-0">
          <summary
            aria-label="Open account menu"
            className="flex h-8 w-8 cursor-pointer list-none items-center justify-center rounded-md text-ink-secondary hover:bg-surface-hover focus-visible:ring-2 focus-visible:ring-accent"
          >
            <Icon name="account" className="h-4 w-4" />
          </summary>
          <div className="absolute right-0 top-10 z-50 w-64 border border-line bg-surface p-3 shadow-lg">
            <UserProfileMenu />
          </div>
        </details>
      </div>

      <nav
        aria-label="Case workspace views"
        role="tablist"
        className="flex min-h-10 gap-5 overflow-x-auto px-4 text-[11px] sm:px-5 lg:px-6"
      >
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
                selected
                  ? "border-accent text-accent"
                  : "border-transparent text-ink-muted hover:text-ink"
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

/** The title, while it is being changed.
 *
 * Enter and leaving the field both keep what was typed; Escape abandons it.
 * The field starts selected, because renaming usually means replacing.
 */
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
        className="h-7 w-full min-w-0 rounded border border-accent bg-surface px-2 text-[15px] font-semibold tracking-[-0.015em] text-ink outline-none focus:ring-2 focus:ring-accent/25 sm:text-base"
      />
    </form>
  );
}
