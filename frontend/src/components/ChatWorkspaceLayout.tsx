"use client";
import Link from "next/link";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
import { CaseIntakeView } from "@/components/intake/CaseIntakeView";
import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
import { TechnicalContextView } from "@/components/technical/TechnicalContextView";
import { ChatPanel } from "@/components/conversation/ChatPanel";
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
import type { ChatWorkspaceLayoutProps } from "@/features/chat/workspace/chat-workspace-types";

function EmptyStateCaseRequired({
  title,
  subtitle,
  description,
  onOpenIntake,
}: {
  title: string;
  subtitle: string;
  description: string;
  onOpenIntake: () => void;
}) {
  return (
    <div className="flex min-h-0 flex-1 flex-col items-center justify-center p-6 text-center bg-canvas">
      <div className="max-w-md space-y-4 rounded-xl border border-line bg-surface p-8 shadow-xs">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-surface-nested text-ink">
          <Icon name="intake" className="h-5 w-5" />
        </span>
        <div className="space-y-1">
          <h2 className="text-base font-bold text-ink">{title}</h2>
          <p className="text-xs font-semibold text-ink-secondary">{subtitle}</p>
          <p className="text-xs text-ink-muted leading-relaxed pt-1">{description}</p>
        </div>
        <button
          type="button"
          onClick={onOpenIntake}
          className="inline-flex items-center gap-2 rounded bg-primary px-5 py-2.5 text-xs font-bold text-ivory transition-colors hover:bg-charcoal-hover active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary"
        >
          <Icon name="intake" className="h-3.5 w-3.5" />
          <span>Go to Case Intake · เปิดสำนวนคดี</span>
        </button>
      </div>
    </div>
  );
}

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
  hasCompletedAnalysis,
  messages,
  deleteCandidate,
  onSelectThread,
  onNewChat,
  onRequestDelete,
  onViewChange,
  onInputChange,
  onPostAnswerActionChange,
  onSubmit,
  onSetDeleteCandidate,
  onCancelDelete,
  onConfirmDelete,
  onNavigateToSource,
  onSubmitCase,
}: ChatWorkspaceLayoutProps) {
  const displayThreadTitle =
    activeThread?.title === "New chat" || !activeThread?.title
      ? "New case"
      : activeThread.title;

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
                  {displayThreadTitle}
                </p>
                <p className="mt-0.5 flex items-center gap-1.5 text-xs font-medium text-ink-secondary">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      phase === "error"
                        ? "bg-accent"
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
            <div className="flex w-full items-center gap-2 md:hidden">
              <label htmlFor="mobile-workspace-view" className="sr-only">
                Select workspace
              </label>
              <select
                id="mobile-workspace-view"
                value={activeView}
                onChange={(event) => onViewChange(event.target.value as WorkspaceView)}
                aria-label="Select workspace"
                className="min-h-11 min-w-0 flex-1 rounded-xl border border-line bg-surface px-3 text-sm font-semibold text-ink outline-none hover:border-ink focus-visible:ring-2 focus-visible:ring-primary disabled:bg-control-disabled disabled:text-ink-disabled"
              >
                <option value="intake">Intake</option>
                <option value="overview">Overview</option>
                <option value="materials">Case Materials</option>
                <option value="technical-context">Technical Context</option>
                <option value="chat">Chat</option>
                <option value="report">Report</option>
              </select>
            </div>
            <div className="flex w-full items-center gap-2 md:hidden">
              <select
                value={activeThreadId ?? ""}
                onChange={(event) => {
                  if (event.target.value) onSelectThread(event.target.value);
                }}
                aria-label="Select saved case"
                className="min-h-11 min-w-0 flex-1 rounded-xl border border-line bg-surface px-3 text-sm font-semibold text-ink outline-none hover:border-ink focus-visible:ring-2 focus-visible:ring-primary disabled:bg-control-disabled disabled:text-ink-disabled"
              >
                <option value="">Select case</option>
                {threads.map((thread) => {
                  const itemTitle = thread.title === "New chat" ? "New case" : thread.title;
                  return (
                    <option key={thread.id} value={thread.id}>
                      {itemTitle}
                    </option>
                  );
                })}
              </select>
              <button
                type="button"
                onClick={onNewChat}
                disabled={creatingThread}
                aria-label="New case"
                title="New case"
                className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-line bg-surface text-ink outline-none transition-colors hover:border-ink hover:bg-surface-hover active:bg-control-disabled focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
              >
                <Icon name="plus" className="h-5 w-5" />
              </button>
              {activeThread && (
                <button
                  type="button"
                  onClick={() => onSetDeleteCandidate(activeThread)}
                  disabled={deletingThreadId !== null}
                  aria-label={`Delete ${displayThreadTitle}`}
                  title={`Delete ${displayThreadTitle}`}
                  className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-line bg-surface text-ink-secondary outline-none transition-colors hover:border-accent hover:bg-accent-soft hover:text-accent focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-wait disabled:bg-control-disabled disabled:text-ink-disabled"
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
                  className="mx-4 mt-4 shrink-0 rounded-lg border border-accent/30 bg-accent-soft px-4 py-3 text-xs font-medium text-accent sm:mx-7 lg:mx-10"
                >
                  {queryError}
                </div>
              )}
              {activeWorkspaceView === "intake" ? (
                <CaseIntakeView
                  isSubmitting={phase === "querying" || phase === "analyzing"}
                  error={queryError}
                  onSubmitCase={onSubmitCase ?? (() => {})}
                  messages={messages}
                  onOpenOverview={() => onViewChange("overview")}
                  onOpenChat={() => onViewChange("chat")}
                />
              ) : activeWorkspaceView === "overview" ? (
                messages.length === 0 ? (
                  <EmptyStateCaseRequired
                    title="Case Overview"
                    subtitle="ยังไม่มีข้อมูลสำนวนคดี (No Case Narrative)"
                    description="กรุณากรอกรายละเอียดเหตุการณ์ในหน้า Case Intake เพื่อให้ CyberCase วิเคราะห์และจัดทำภาพรวมสำนวนคดี"
                    onOpenIntake={() => onViewChange("intake")}
                  />
                ) : (
                  <CaseOverviewView
                    threadId={activeThreadId}
                    threadTitle={displayThreadTitle}
                    threadStatus={threadStatus ?? "idle"}
                    messages={messages}
                    onOpenChat={() => onViewChange("chat")}
                    onOpenReport={() => onViewChange("report")}
                    onOpenMaterials={() => onViewChange("materials")}
                    onOpenTechnicalContext={() => onViewChange("technical-context")}
                    onNavigateToSource={onNavigateToSource}
                  />
                )
              ) : activeWorkspaceView === "materials" ? (
                <CaseMaterialsView
                  messages={messages}
                  onOpenChat={() => onViewChange("chat")}
                  onOpenIntake={() => onViewChange("intake")}
                />
              ) : activeWorkspaceView === "technical-context" ? (
                <TechnicalContextView
                  messages={messages}
                  onOpenIntake={() => onViewChange("intake")}
                  onNavigateToSource={onNavigateToSource}
                />
              ) : activeWorkspaceView === "chat" ? (
                <div
                  id="workspace-chat-panel"
                  role="tabpanel"
                  aria-label="Chat"
                  className="flex min-h-0 flex-1 flex-col overflow-hidden"
                >
                  {messages.length === 0 && (
                    <div className="border-b border-line bg-surface-nested/40 px-4 py-2.5 text-xs text-ink-secondary flex items-center justify-between gap-3">
                      <p className="truncate">
                        💡 ยังไม่ได้บันทึกรายละเอียดสำนวนคดี — แนะนำให้เริ่มที่หน้า Intake เพื่อให้ระบบเชื่อมโยง MITRE ATT&amp;CK
                      </p>
                      <button
                        type="button"
                        onClick={() => onViewChange("intake")}
                        className="shrink-0 font-bold text-primary hover:underline text-[11px]"
                      >
                        เปิด Case Intake →
                      </button>
                    </div>
                  )}
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
                  />
                </div>
              ) : (
                <ChatReportView
                  key={`${activeThreadId ?? "new-case"}:${messages.at(-1)?.id ?? "empty"}`}
                  threadId={activeThreadId}
                  threadTitle={displayThreadTitle}
                  threadStatus={threadStatus}
                  hasMessages={messages.length > 0}
                  hasCompletedAnalysis={hasCompletedAnalysis}
                  onOpenChat={() => onViewChange("chat")}
                  onOpenOverview={() => onViewChange("overview")}
                />
              )}
            </main>
          </div>
        </div>
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
