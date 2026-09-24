"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { CyberCaseLogo } from "@/components/CyberCaseLogo";
import { Icon } from "@/components/icons";
import { AccountMenu } from "@/features/auth/AccountMenu";
import type { CaseRead } from "@/lib/api";
import { workspaceViewDescriptions, type WorkspaceView } from "./routes";

interface WorkspaceHeaderProps {
  activeCase: CaseRead | null;
  activeView: WorkspaceView;
  creatingCase: boolean;
  isAnalyzing: boolean;
  isStale: boolean;
  onViewChange: (view: WorkspaceView) => void;
  onNewCase: () => void;
  onRenameCase?: (title: string) => void;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
}

const workspaceTabs: Array<{ view: WorkspaceView; label: string }> = [
  { view: "sources", label: "Sources" },
  { view: "analysis", label: "Analysis" },
  { view: "legal", label: "Legal" },
];

export function WorkspaceHeader({
  activeCase,
  activeView,
  creatingCase,
  isAnalyzing,
  isStale,
  onViewChange,
  onNewCase,
  onRenameCase,
  isChatOpen = true,
  onToggleChat,
}: WorkspaceHeaderProps) {
  const [renaming, setRenaming] = useState(false);
  const displayCaseTitle = activeCase?.title || "New case";
  const analysisMarker = isAnalyzing
    ? "bg-accent motion-safe:animate-pulse"
    : isStale
      ? "bg-unresolved"
      : null;

  return (
    <header className="shrink-0 border-b border-line bg-surface">
      <div className="flex flex-wrap items-center gap-x-2 px-3 sm:px-4 lg:px-5">
        <Link
          href="/case"
          aria-label="All cases"
          title="All cases"
          className="order-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg transition-colors hover:bg-surface-hover"
        >
          <CyberCaseLogo size={26} />
        </Link>

        <div className="group order-2 flex h-14 min-w-0 flex-1 items-center gap-1 md:max-w-[min(42vw,34rem)] md:flex-none">
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
                className="truncate text-[15px] font-semibold tracking-[-0.01em] text-ink"
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
                  className="icon-btn h-7 w-7 opacity-0 group-hover:opacity-100 focus-visible:opacity-100 max-md:opacity-100"
                >
                  <Icon name="edit" className="h-3.5 w-3.5" />
                </button>
              )}
            </>
          )}
        </div>

        <nav
          aria-label="Case workspace views"
          role="tablist"
          className="order-4 -mx-1 flex h-11 w-full items-center gap-1 overflow-x-auto md:order-3 md:mx-0 md:ml-3 md:h-14 md:w-auto"
        >
          {workspaceTabs.map((item) => {
            const selected = item.view === activeView;
            const marker = item.view === "analysis" ? analysisMarker : null;
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
                className={`inline-flex h-8 shrink-0 items-center gap-1.5 rounded-lg px-3 text-[13px] font-medium transition-colors ${
                  selected
                    ? "bg-surface-nested text-ink"
                    : "text-ink-muted hover:bg-surface-hover hover:text-ink"
                }`}
              >
                {item.label}
                {marker && (
                  <span className={`h-1.5 w-1.5 rounded-full ${marker}`} aria-hidden="true" />
                )}
              </button>
            );
          })}
        </nav>

        <div className="order-3 ml-auto flex h-14 shrink-0 items-center gap-1.5 md:order-4">
          {onToggleChat && (
            <button
              type="button"
              onClick={onToggleChat}
              aria-label={isChatOpen ? "Close Ask" : "Open Ask"}
              title={isChatOpen ? "Close Ask" : "Open Ask"}
              aria-pressed={isChatOpen}
              className={`inline-flex h-8 shrink-0 items-center gap-1.5 rounded-lg px-2.5 text-[13px] font-semibold transition-colors ${
                isChatOpen
                  ? "bg-surface-nested text-ink"
                  : "text-ink-secondary hover:bg-surface-hover hover:text-ink"
              }`}
            >
              <Icon name="chat" className="h-4 w-4" />
              <span className="hidden sm:inline">Ask</span>
            </button>
          )}

          <AccountMenu
            actions={[
              { label: "All cases", icon: "folder", href: "/case" },
              { label: "New case", icon: "plus", onSelect: onNewCase, disabled: creatingCase },
            ]}
          />
        </div>
      </div>
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
        className="h-8 w-full min-w-0 rounded-lg border border-line-strong bg-surface px-2 text-[15px] font-semibold tracking-[-0.01em] text-ink outline-none focus:border-ink"
      />
    </form>
  );
}
