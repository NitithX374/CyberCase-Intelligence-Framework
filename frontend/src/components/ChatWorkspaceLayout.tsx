"use client";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
import { CaseIntakeView } from "@/components/intake/CaseIntakeView";
import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
import { TechnicalContextView } from "@/components/technical/TechnicalContextView";
import { ChatPanel } from "@/components/conversation/ChatPanel";
import { ChatReportView } from "@/components/report/ChatReportView";
import { DeleteChatDialog } from "@/components/common/DeleteChatDialog";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import {
  EmptyChatIntakeNotice,
  EmptyStateCaseRequired,
} from "@/components/common/CaseRequiredState";
import { toUserFacingError } from "@/lib/user-facing-error";
import { WorkspaceSidebar } from "@/components/layout/WorkspaceSidebar";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import type { ChatWorkspaceLayoutProps } from "@/features/chat/workspace/chat-workspace-types";

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
  onClearQueryError,
  onRetryQuery,
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
          <WorkspaceHeader
            activeThread={activeThread}
            activeThreadId={activeThreadId}
            activeView={activeView}
            threads={threads}
            creatingThread={creatingThread}
            deletingThreadId={deletingThreadId}
            phase={phase}
            onViewChange={onViewChange}
            onSelectThread={onSelectThread}
            onNewChat={onNewChat}
            onRequestDelete={onSetDeleteCandidate}
          />
          <div className="flex min-h-0 flex-1 overflow-hidden bg-canvas">
            <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
              {activeWorkspaceView === "intake" ? (
                <CaseIntakeView
                  caseKey={activeThreadId ?? "draft"}
                  threadId={activeThreadId}
                  isSubmitting={phase === "querying" || phase === "analyzing"}
                  error={null}
                  onSubmitCase={onSubmitCase ?? (() => {})}
                  messages={messages}
                  onOpenOverview={() => onViewChange("overview")}
                  onOpenChat={() => onViewChange("chat")}
                  onOpenMaterials={() => onViewChange("materials")}
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
                    onOpenIntake={() => onViewChange("intake")}
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
                    <EmptyChatIntakeNotice onOpenIntake={() => onViewChange("intake")} />
                  )}
                  <ChatPanel
                    messages={visibleMessages}
                    input={input}
                    threadStatus={threadStatus}
                    phase={phase}
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
      <MeaningfulErrorModal
        isOpen={Boolean(queryError)}
        error={
          queryError
            ? toUserFacingError(queryError, {
                isUncertain: phase === "querying" || phase === "analyzing",
              })
            : null
        }
        onClose={onClearQueryError ?? (() => {})}
        onRetry={onRetryQuery}
      />
    </div>
  );
}
