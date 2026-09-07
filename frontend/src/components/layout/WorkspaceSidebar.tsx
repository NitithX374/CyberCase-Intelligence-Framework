"use client";

import Link from "next/link";
import { CyberCaseLogo } from "@/components/common/CyberCaseLogo";
import type { ChatThreadRead } from "@/lib/api";
import { Icon, type IconName } from "@/components/common/icons";
import {
  workspaceViewDescriptions,
  workspaceViewLabels,
  type WorkspaceView,
} from "@/components/common/types";

interface WorkspaceNavigationProps {
  threads: ChatThreadRead[];
  activeThreadId: string | null;
  threadsLoading: boolean;
  threadsError: string | null;
  onSelectThread: (threadId: string) => void;
  onNewChat: () => void;
  onRequestDelete: (thread: ChatThreadRead) => void;
  deletingThreadId: string | null;
  activeView: WorkspaceView;
  onViewChange: (view: WorkspaceView) => void;
}

const threadStatusConfig: Record<
  ChatThreadRead["status"],
  { label: string; dotClass: string }
> = {
  idle: { label: "Ready", dotClass: "bg-ink-muted" },
  processing: {
    label: "Analyzing",
    dotClass: "bg-evidence motion-safe:animate-pulse motion-reduce:animate-none",
  },
  awaiting_followup: { label: "Your input is needed", dotClass: "bg-unresolved" },
  answered: { label: "Analysis available", dotClass: "bg-established" },
  failed: { label: "Needs attention", dotClass: "bg-critical" },
};

const reviewTabs: Array<{ view: WorkspaceView; icon: IconName }> = [
  { view: "intake", icon: "intake" },
  { view: "overview", icon: "overview" },
  { view: "materials", icon: "materials" },
  { view: "report", icon: "report" },
];

const toolTabs: Array<{ view: WorkspaceView; icon: IconName }> = [
  { view: "technical-context", icon: "technical" },
];

export function WorkspaceSidebar({
  threads,
  activeThreadId,
  threadsLoading,
  threadsError,
  onSelectThread,
  onNewChat,
  onRequestDelete,
  deletingThreadId,
  activeView,
  onViewChange,
}: WorkspaceNavigationProps) {
  return (
    <aside className="hidden h-full w-60 shrink-0 flex-col border-r border-line bg-sidebar md:flex">
      <div className="px-4 pb-4 pt-4">
        <Link
          href="/"
          aria-label="CyberCase home"
          className="flex items-center gap-2.5 rounded-lg outline-none transition-colors hover:text-accent focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 motion-reduce:transition-none"
        >
          <CyberCaseLogo size={32} />
          <span className="text-sm font-extrabold tracking-[-0.02em] text-ink">
            CyberCase
          </span>
        </Link>
        <p className="mt-3 pl-0.5 text-[9px] font-bold uppercase tracking-[0.16em] text-ink-muted">
          Analytical workspace
        </p>
      </div>

      <div className="px-3">
        <button
          type="button"
          onClick={onNewChat}
          className="flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-primary px-3 text-xs font-bold text-ivory outline-none transition-colors duration-150 hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 motion-reduce:transition-none"
        >
          <Icon name="plus" className="h-3.5 w-3.5 shrink-0" />
          <span>New case</span>
        </button>
      </div>

      <div className="space-y-5 px-3 pt-5">
        <NavigationGroup
          label="Case"
          tabs={reviewTabs}
          activeView={activeView}
          onViewChange={onViewChange}
        />
        <NavigationGroup
          label="Tools"
          tabs={toolTabs}
          activeView={activeView}
          onViewChange={onViewChange}
        />
      </div>

      <section
        aria-label="Saved cases"
        className="min-h-0 flex-1 overflow-y-auto px-3 pb-3 pt-6"
      >
        <div className="flex items-center justify-between px-1">
          <p className="section-eyebrow">Recent cases</p>
          {threads.length > 0 && (
            <span className="rounded-full bg-surface-hover px-1.5 py-0.5 text-[9px] font-bold text-ink-secondary">
              {threads.length}
            </span>
          )}
        </div>

        {threadsLoading ? (
          <p className="mt-3 px-1 text-xs text-ink-secondary" role="status">
            Loading…
          </p>
        ) : threadsError ? (
          <p className="mt-3 break-words px-1 text-xs leading-5 text-accent">
            ไม่สามารถโหลดรายการคดีได้
          </p>
        ) : threads.length === 0 ? (
          <p className="mt-3 px-1 text-xs leading-5 text-ink-secondary">
            No saved cases yet.
          </p>
        ) : (
          <div className="mt-2 space-y-1">
            {threads.map((thread) => {
              const selected = thread.id === activeThreadId;
              const statusInfo = threadStatusConfig[thread.status];
              const displayTitle = thread.title === "New chat" ? "New case" : thread.title;
              return (
                <div key={thread.id} className="group flex items-center gap-1">
                  <button
                    type="button"
                    aria-current={selected ? "page" : undefined}
                    aria-label={`${displayTitle}, ${statusInfo.label}`}
                    title={displayTitle}
                    onClick={() => onSelectThread(thread.id)}
                    className={`relative flex min-h-9 min-w-0 flex-1 items-center gap-2 rounded-lg border-l-2 px-2.5 py-1.5 text-left outline-none transition-[background-color,border-color,color] duration-150 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1 motion-reduce:transition-none ${
                      selected
                        ? "border-l-accent bg-surface text-ink shadow-[0_1px_2px_rgba(39,39,39,0.04)]"
                        : "border-l-transparent text-ink-secondary hover:bg-surface/70 hover:text-ink"
                    }`}
                  >
                    <span
                      className={`h-1.5 w-1.5 shrink-0 rounded-full ${statusInfo.dotClass}`}
                      aria-hidden="true"
                    />
                    <span className="block min-w-0 flex-1 truncate text-[11.5px] leading-tight">
                      {displayTitle}
                    </span>
                  </button>
                  <button
                    type="button"
                    aria-label={`Delete ${displayTitle}`}
                    title={`Delete ${displayTitle}`}
                    disabled={deletingThreadId !== null}
                    onClick={() => onRequestDelete(thread)}
                    className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-ink-secondary opacity-0 outline-none transition-[opacity,background-color,color] duration-150 hover:bg-accent-soft hover:text-accent focus:opacity-100 focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-wait disabled:text-ink-disabled disabled:opacity-40 group-hover:opacity-100 group-focus-within:opacity-100 motion-reduce:transition-none"
                  >
                    <Icon name="trash" className="h-3 w-3" />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </aside>
  );
}

function NavigationGroup({
  label,
  tabs,
  activeView,
  onViewChange,
}: {
  label: string;
  tabs: Array<{ view: WorkspaceView; icon: IconName }>;
  activeView: WorkspaceView;
  onViewChange: (view: WorkspaceView) => void;
}) {
  return (
    <div>
      <p className="px-1 text-[9px] font-extrabold uppercase tracking-[0.16em] text-ink-muted">
        {label}
      </p>
      <nav
        aria-label={`${label} workspace views`}
        role="tablist"
        className="mt-1.5 space-y-0.5"
      >
        {tabs.map(({ view, icon }) => {
          const selected = view === activeView;
          return (
            <button
              key={view}
              id={`workspace-tab-${view}`}
              type="button"
              role="tab"
              aria-selected={selected}
              aria-controls={`workspace-${view}-panel`}
              tabIndex={selected ? 0 : -1}
              title={workspaceViewDescriptions[view]}
              onClick={() => onViewChange(view)}
              className={`group flex min-h-9 w-full items-center gap-2.5 rounded-lg border-l-2 px-2.5 text-left text-xs font-semibold outline-none transition-[background-color,border-color,color] duration-150 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1 motion-reduce:transition-none ${
                selected
                  ? "border-l-accent bg-surface font-bold text-ink"
                  : "border-l-transparent text-ink-secondary hover:bg-surface/70 hover:text-ink"
              }`}
            >
              <Icon
                name={icon}
                className={`h-3.5 w-3.5 shrink-0 ${
                  selected ? "text-accent" : "text-ink-secondary group-hover:text-ink"
                }`}
              />
              <span className="truncate">{workspaceViewLabels[view]}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
