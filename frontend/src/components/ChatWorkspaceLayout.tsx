"use client";
import Link from "next/link";
import { ChatPanel } from "@/components/conversation/ChatPanel";
import { CaseStateInspector } from "@/components/conversation/CaseStateInspector";
import { ChatExtractionView } from "@/components/analysis/ChatExtractionView";
import { ChatRelationshipsView } from "@/components/relationships/ChatRelationshipsView";
import { ChatReportView } from "@/components/report/ChatReportView";
import { DeleteChatDialog } from "@/components/common/DeleteChatDialog";
import { Icon } from "@/components/common/icons";
import { WorkspaceSidebar } from "@/components/layout/WorkspaceSidebar";
import {
  workspaceViewLabels,
  type RunPhase,
  type WorkspaceView,
} from "@/components/common/types";
const phaseLabels: Record<RunPhase, string> = {
  idle: "Ready",
  querying: "Processing",
  awaiting_followup: "Follow-up required",
  analyzing: "Validating",
  ready: "Complete",
  error: "Error",
};
import type { ChatWorkspaceLayoutProps } from "@/features/chat/workspace/chat-workspace-layout-types";

export function ChatWorkspaceLayout({
  activeThread,
  activeThreadId,
  activeView,
  activeWorkspaceView,
  threads,
  threadsLoading,
  threadsError,
  creatingThread,
  deletingThreadId,
  phase,
  threadStatus,
  queryError,
  input,
  postAnswerAction,
  visibleMessages,
  latestExtraction,
  hasValidatedExtraction,
  messages,
  caseUpdates,
  deleteCandidate,
  selectedCaseUpdateOrdinal,
  isCaseInspectorOpen,
  onSelectThread,
  onNewChat,
  onRequestDelete,
  onViewChange,
  onInputChange,
  onPostAnswerActionChange,
  onSubmit,
  onSelectMessageOrdinal,
  onSetDeleteCandidate,
  onCancelDelete,
  onConfirmDelete,
  onSelectCaseUpdateOrdinal,
  onSetCaseInspectorOpen,
}: ChatWorkspaceLayoutProps) {
  return (
    <div className="flex h-dvh overflow-hidden bg-canvas text-ink">
      <WorkspaceSidebar
        threads={threads}
        activeThreadId={activeThreadId}
        threadsLoading={threadsLoading}
        threadsError={threadsError}
        onSelectThread={onSelectThread}
        onNewChat={onNewChat}
        onRequestDelete={onRequestDelete}
        deletingThreadId={deletingThreadId}
        activeView={activeView}
        onViewChange={onViewChange}
      />
      <div className="flex min-w-0 flex-1 overflow-hidden">
        <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
          <header className="flex min-h-[76px] shrink-0 flex-wrap items-center gap-3 border-b border-line bg-canvas px-3 py-3 sm:px-5 md:min-h-[72px] md:flex-nowrap md:px-7">
            <div className="flex min-w-0 w-full items-center gap-3 md:flex-1">
              <Link
                href="/"
                aria-label="CyberCase home"
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[10px] bg-primary text-sm font-extrabold text-ivory outline-none transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 md:hidden"
              >
                C
              </Link>
              <div className="min-w-0 flex-1">
                <p className="truncate text-base font-extrabold tracking-[-0.02em] sm:text-lg">
                  {activeThread?.title ?? "New chat"}
                </p>
                <p className="mt-0.5 flex items-center gap-1.5 text-xs font-medium text-ink-secondary">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      phase === "error"
                        ? "bg-[#B42318]"
                        : phase === "querying" || phase === "analyzing"
                          ? "bg-primary motion-safe:animate-pulse"
                          : "bg-ink-muted"
                    }`}
                  />
                  <span>{workspaceViewLabels[activeView]}</span>
                  <span aria-hidden="true">·</span>
                  <span>{phaseLabels[phase]}</span>
                </p>
              </div>
            </div>
            {activeWorkspaceView === "chat" && (
              <div className="hidden md:flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => onSetCaseInspectorOpen(!isCaseInspectorOpen)}
                  aria-label={
                    isCaseInspectorOpen
                      ? "Hide Case State Inspector"
                      : "Show Case State Inspector"
                  }
                  title="Toggle Case State Inspector"
                  className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-bold transition-colors cursor-pointer ${
                    isCaseInspectorOpen
                      ? "border-primary bg-primary text-ivory shadow-xs"
                      : "border-line-strong bg-surface text-ink-secondary hover:border-primary hover:text-ink"
                  }`}
                >
                  <Icon name="details" className="h-4 w-4" />
                  <span>
                    Case State {caseUpdates.length > 0 ? `(${caseUpdates.length})` : ""}
                  </span>
                </button>
              </div>
            )}
            <div className="flex w-full items-center gap-2 md:hidden">
              <label htmlFor="mobile-workspace-view" className="sr-only">
                Select workspace
              </label>
              <select
                id="mobile-workspace-view"
                value={activeView}
                onChange={(event) => onViewChange(event.target.value as WorkspaceView)}
                aria-label="Select workspace"
                className="min-h-11 min-w-0 flex-1 rounded-xl border border-line-strong bg-surface px-3 text-sm font-semibold text-ink outline-none hover:border-primary focus-visible:ring-2 focus-visible:ring-primary disabled:bg-control-disabled disabled:text-ink-disabled"
              >
                <option value="chat">Chat</option>
                <option value="extraction">Case details</option>
                <option value="relationships">Relationships</option>
                <option value="report">Report generation</option>
              </select>
            </div>
            <div className="flex w-full items-center gap-2 md:hidden">
              <select
                value={activeThreadId ?? ""}
                onChange={(event) => {
                  if (event.target.value) onSelectThread(event.target.value);
                }}
                aria-label="Select saved chat"
                className="min-h-11 min-w-0 flex-1 rounded-xl border border-line-strong bg-surface px-3 text-sm font-semibold text-ink outline-none hover:border-primary focus-visible:ring-2 focus-visible:ring-primary disabled:bg-control-disabled disabled:text-ink-disabled"
              >
                <option value="">Select chat</option>
                {threads.map((thread) => (
                  <option key={thread.id} value={thread.id}>
                    {thread.title}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={onNewChat}
                disabled={creatingThread}
                aria-label="New chat"
                title="New chat"
                className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-line-strong bg-surface text-ink outline-none transition-colors hover:border-primary hover:bg-surface-hover active:bg-control-disabled focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
              >
                <Icon name="plus" className="h-5 w-5" />
              </button>
              {activeThread && (
                <button
                  type="button"
                  onClick={() => onSetDeleteCandidate(activeThread)}
                  disabled={deletingThreadId !== null}
                  aria-label={`Delete ${activeThread.title}`}
                  title={`Delete ${activeThread.title}`}
                  className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-line-strong bg-surface text-ink-secondary outline-none transition-colors hover:border-[#B42318] hover:bg-red-50 hover:text-[#B42318] focus-visible:ring-2 focus-visible:ring-[#B42318] disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
                >
                  <Icon name="trash" className="h-5 w-5" />
                </button>
              )}
            </div>
          </header>
          <div className="flex min-h-0 flex-1 overflow-hidden bg-canvas">
            <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
              {activeWorkspaceView !== "chat" && queryError && (
                <div
                  role="alert"
                  className="mx-4 mt-4 shrink-0 rounded-xl border border-[#E5B8B3] bg-[#FFF5F4] px-4 py-3 text-sm font-medium text-[#8F1D14] sm:mx-7 lg:mx-10"
                >
                  {queryError}
                </div>
              )}
              {activeWorkspaceView === "chat" ? (
                <div
                  id="workspace-chat-panel"
                  role="tabpanel"
                  aria-label="Chat"
                  className="flex min-h-0 flex-1 flex-col overflow-hidden"
                >
                  <ChatPanel
                    messages={visibleMessages}
                    input={input}
                    threadStatus={threadStatus}
                    phase={phase}
                    error={queryError}
                    postAnswerAction={postAnswerAction}
                    onInputChange={onInputChange}
                    onPostAnswerActionChange={onPostAnswerActionChange}
                    onSubmit={onSubmit}
                    onSelectMessageOrdinal={onSelectMessageOrdinal}
                  />
                </div>
              ) : activeView === "relationships" ? (
                <ChatRelationshipsView
                  extraction={latestExtraction}
                  onOpenChat={() => onViewChange("chat")}
                />
              ) : activeWorkspaceView === "extraction" ? (
                <ChatExtractionView
                  extraction={latestExtraction}
                  onOpenChat={() => onViewChange("chat")}
                />
              ) : (
                <ChatReportView
                  key={`${activeThreadId ?? "new-chat"}:${messages.at(-1)?.id ?? "empty"}`}
                  threadId={activeThreadId}
                  threadTitle={activeThread?.title ?? "New chat"}
                  threadStatus={threadStatus}
                  hasMessages={messages.length > 0}
                  hasValidatedExtraction={hasValidatedExtraction}
                  onOpenChat={() => onViewChange("chat")}
                />
              )}
            </main>
          </div>
        </div>
        {activeWorkspaceView === "chat" && (
          <CaseStateInspector
            updates={caseUpdates}
            selectedOrdinal={selectedCaseUpdateOrdinal}
            onSelectOrdinal={onSelectCaseUpdateOrdinal}
            isOpen={isCaseInspectorOpen}
            onClose={() => onSetCaseInspectorOpen(false)}
          />
        )}
      </div>
      <DeleteChatDialog
        thread={deleteCandidate}
        isDeleting={deletingThreadId !== null}
        onCancel={onCancelDelete}
        onConfirm={onConfirmDelete}
      />
    </div>
  );
}
