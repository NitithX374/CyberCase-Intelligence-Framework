"use client";

import type { FormEvent } from "react";
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
  if (!isOpen) return null;

  return (
    <aside
      id="workspace-chat-panel"
      role="complementary"
      aria-label="Case Chat Assistant"
      className="fixed inset-0 z-50 flex h-full w-full shrink-0 flex-col overflow-hidden border-l border-line bg-surface md:static md:z-auto md:w-[clamp(22rem,34vw,30rem)]"
    >
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
