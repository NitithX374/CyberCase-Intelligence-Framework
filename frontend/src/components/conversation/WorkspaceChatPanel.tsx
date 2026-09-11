"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { ChatPanel } from "@/components/conversation/ChatPanel";
import { EmptyChatIntakeNotice } from "@/components/common/CaseRequiredState";
import { Icon } from "@/components/common/icons";
import type {
  CaseAnalysisResultRead,
  CaseEvidenceSnapshotRead,
  PersistedChatMessage,
  ThreadStatus,
} from "@/lib/api";
import type {
  RunPhase,
  WorkspaceView,
} from "@/components/common/types";

interface WorkspaceChatPanelProps {
  isOpen: boolean;
  phase: RunPhase;
  messages: PersistedChatMessage[];
  visibleMessages: PersistedChatMessage[];
  threadStatus: ThreadStatus | null;
  input: string;
  hasAnalysisContext: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  leadSnapshot?: CaseEvidenceSnapshotRead | null;
  onViewChange: (view: WorkspaceView) => void;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onToggleChat?: () => void;
}

export function WorkspaceChatPanel({
  isOpen,
  phase,
  messages,
  visibleMessages,
  threadStatus,
  input,
  hasAnalysisContext,
  leadResult,
  leadSnapshot,
  onViewChange,
  onInputChange,
  onSubmit,
  onToggleChat,
}: WorkspaceChatPanelProps) {
  const [chatWidth, setChatWidth] = useState(440);
  const [isResizing, setIsResizing] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  const startResizing = useCallback((event: React.MouseEvent) => {
    event.preventDefault();
    setIsResizing(true);
  }, []);

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (event: MouseEvent) => {
      const newWidth = window.innerWidth - event.clientX;
      if (newWidth >= 340 && newWidth <= Math.min(960, window.innerWidth * 0.75)) {
        setChatWidth(newWidth);
        setIsExpanded(newWidth > 620);
      }
    };
    const handleMouseUp = () => setIsResizing(false);
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
      return;
    }
    const targetWidth = Math.min(760, Math.floor(window.innerWidth * 0.55));
    setChatWidth(Math.max(600, targetWidth));
    setIsExpanded(true);
  };

  if (!isOpen) return null;

  return (
    <aside
      id="workspace-chat-panel"
      role="complementary"
      aria-label="Case Chat Assistant"
      style={{ width: isMobile ? "100%" : `${chatWidth}px` }}
      className={`relative flex h-full shrink-0 flex-col overflow-hidden border-l border-line bg-surface ${isMobile
        ? "fixed inset-0 z-50 w-full"
        : isResizing
          ? "select-none"
          : "transition-[width] duration-75"
      }`}
    >
      {!isMobile && (
        <div
          role="separator"
          aria-orientation="vertical"
          onMouseDown={startResizing}
          className="group absolute -left-1.5 top-0 bottom-0 z-30 w-3 cursor-col-resize select-none transition-colors hover:bg-primary/20"
          title="Drag to resize panel"
        >
          <div className="mx-auto h-full w-px bg-line transition-all group-hover:w-0.5 group-hover:bg-primary" />
        </div>
      )}

      <div className="flex h-[53px] shrink-0 items-center justify-between border-b border-line bg-surface px-4 md:h-[58px]">
        <div className="flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-ivory">
            <Icon name="chat" className="h-3.5 w-3.5" />
          </div>
          <span className="text-xs font-bold uppercase tracking-[0.08em] text-ink">
            Case Chat
          </span>
          <span
            className={`h-2 w-2 rounded-full ${phase === "error"
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
          {onToggleChat && (
            <button
              type="button"
              onClick={onToggleChat}
              aria-label="Close Chat"
              title="Close Chat"
              className="flex h-7 w-7 items-center justify-center rounded-lg text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-primary"
            >
              <Icon name="close" className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

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
          hasAnalysisContext={hasAnalysisContext}
          leadResult={leadResult}
          leadSnapshot={leadSnapshot}
          onOpenOverview={() => onViewChange("overview")}
          onOpenIntake={() => onViewChange("intake")}
          onInputChange={onInputChange}
          onSubmit={onSubmit}
        />
      </div>
    </aside>
  );
}
