"use client";

import { useCallback, useEffect, useState } from "react";
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
import { Icon } from "@/components/common/icons";
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
  isChatOpen = true,
  onToggleChat,
}: ChatWorkspaceLayoutProps) {
  const displayThreadTitle =
    activeThread?.title === "New chat" || !activeThread?.title
      ? "New case"
      : activeThread.title;

  const [chatWidth, setChatWidth] = useState(440);
  const [isResizing, setIsResizing] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  const startResizing = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = window.innerWidth - e.clientX;
      if (newWidth >= 340 && newWidth <= Math.min(960, window.innerWidth * 0.75)) {
        setChatWidth(newWidth);
        setIsExpanded(newWidth > 620);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing]);

  const handleToggleExpand = () => {
    if (isExpanded) {
      setChatWidth(440);
      setIsExpanded(false);
    } else {
      const targetWidth = Math.min(760, Math.floor(window.innerWidth * 0.55));
      setChatWidth(Math.max(600, targetWidth));
      setIsExpanded(true);
    }
  };

  const handleOpenChat = () => {
    if (!isChatOpen && onToggleChat) {
      onToggleChat();
    }
  };

  return (
    <div className="flex h-dvh overflow-hidden bg-canvas text-ink">
      {/* 1. Left Sidebar Navigation */}
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

      {/* 2. Middle Work Area (WorkspaceHeader on top, Document view scrollable below) */}
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
          isChatOpen={isChatOpen}
          onToggleChat={onToggleChat}
        />

        <main className="flex min-w-0 flex-1 flex-col overflow-y-auto bg-canvas">
          {activeWorkspaceView === "intake" ? (
            <CaseIntakeView
              caseKey={activeThreadId ?? "draft"}
              threadId={activeThreadId}
              threadStatus={threadStatus}
              isSubmitting={phase === "querying" || phase === "analyzing"}
              error={null}
              onSubmitCase={onSubmitCase ?? (() => {})}
              messages={messages}
              onOpenOverview={() => onViewChange("overview")}
              onOpenChat={handleOpenChat}
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
                onOpenChat={handleOpenChat}
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
              onOpenChat={handleOpenChat}
              onOpenIntake={() => onViewChange("intake")}
            />
          ) : activeWorkspaceView === "technical-context" ? (
            <TechnicalContextView
              messages={messages}
              onOpenIntake={() => onViewChange("intake")}
              onNavigateToSource={onNavigateToSource}
            />
          ) : (
            <ChatReportView
              key={`${activeThreadId ?? "new-case"}:${messages.at(-1)?.id ?? "empty"}`}
              threadId={activeThreadId}
              threadTitle={displayThreadTitle}
              threadStatus={threadStatus}
              hasMessages={messages.length > 0}
              hasCompletedAnalysis={hasCompletedAnalysis}
              onOpenChat={handleOpenChat}
              onOpenOverview={() => onViewChange("overview")}
            />
          )}
        </main>
      </div>

      {/* 3. Right Copilot Panel: Full Height (กินพื้นที่ตั้งแต่ข้างบนสุดถึงล่างสุด) + Expandable */}
      {isChatOpen && (
        <aside
          id="workspace-chat-panel"
          role="complementary"
          aria-label="Case Chat Assistant"
          style={{ width: isMobile ? "100%" : `${chatWidth}px` }}
          className={`relative flex h-full shrink-0 flex-col border-l border-line bg-surface overflow-hidden ${
            isMobile
              ? "fixed inset-0 z-50 w-full"
              : isResizing
                ? "select-none"
                : "transition-[width] duration-75"
          }`}
        >
          {/* Drag Handle to Resize Width */}
          {!isMobile && (
            <div
              role="separator"
              aria-orientation="vertical"
              onMouseDown={startResizing}
              className="group absolute -left-1.5 top-0 bottom-0 z-30 w-3 cursor-col-resize hover:bg-primary/20 transition-colors select-none"
              title="Drag to resize panel"
            >
              <div className="mx-auto h-full w-[1px] bg-line group-hover:w-[2px] group-hover:bg-primary transition-all" />
            </div>
          )}

          {/* Copilot Header (Level with WorkspaceHeader at the very top of the window) */}
          <div className="flex h-[53px] md:h-[58px] shrink-0 items-center justify-between border-b border-line bg-surface px-4">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-ivory">
                <Icon name="chat" className="h-3.5 w-3.5" />
              </div>
              <span className="text-xs font-bold uppercase tracking-[0.08em] text-ink">
                CyberCase Copilot
              </span>
              <span
                className={`h-2 w-2 rounded-full ${
                  phase === "error"
                    ? "bg-critical"
                    : phase === "querying" || phase === "analyzing"
                      ? "bg-evidence motion-safe:animate-pulse motion-reduce:animate-none"
                      : phase === "awaiting_followup"
                        ? "bg-unresolved motion-safe:animate-ping"
                        : "bg-established"
                }`}
                title={`Status: ${phase}`}
              />
            </div>

            <div className="flex items-center gap-1">
              {/* Expand / Collapse Width Toggle */}
              {!isMobile && (
                <button
                  type="button"
                  onClick={handleToggleExpand}
                  aria-label={isExpanded ? "Collapse width" : "Expand width"}
                  title={isExpanded ? "Collapse width (440px)" : "Expand width (760px)"}
                  className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-primary"
                >
                  <Icon name={isExpanded ? "collapse" : "expand"} className="h-3.5 w-3.5" />
                </button>
              )}

              {/* Close Button */}
              {onToggleChat && (
                <button
                  type="button"
                  onClick={onToggleChat}
                  aria-label="Close Copilot"
                  title="Close Copilot"
                  className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-primary"
                >
                  <Icon name="close" className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>

          {/* Copilot Chat Body */}
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
            {messages.length === 0 && (
              <div className="p-3">
                <EmptyChatIntakeNotice onOpenIntake={() => onViewChange("intake")} />
              </div>
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
        </aside>
      )}

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
