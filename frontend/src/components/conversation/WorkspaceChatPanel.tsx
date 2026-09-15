"use client";

import { useEffect, useRef, type FormEvent } from "react";
import { ChatPanel } from "@/components/conversation/ChatPanel";
import { EmptyChatIntakeNotice } from "@/components/common/CaseRequiredState";
import { Icon } from "@/components/common/icons";
import type {
  CaseAnalysisResultRead,
  CaseChatStatus,
  EvidenceSourceRead,
  PersistedChatMessage,
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
  chatStatus: CaseChatStatus | null;
  input: string;
  hasAnalysisContext: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  evidenceSources?: EvidenceSourceRead[] | null;
  onViewChange: (view: WorkspaceView) => void;
  onNavigateToSource?: (messageId: string) => void;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onToggleChat?: () => void;
}

export function WorkspaceChatPanel({
  isOpen,
  phase,
  messages,
  visibleMessages,
  chatStatus,
  input,
  hasAnalysisContext,
  leadResult,
  evidenceSources,
  onViewChange,
  onNavigateToSource,
  onInputChange,
  onSubmit,
  onToggleChat,
}: WorkspaceChatPanelProps) {
  const closeButtonRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (isOpen) closeButtonRef.current?.focus();
  }, [isOpen]);

  if (!isOpen) return null;

  const evidenceRevisionLabel = leadResult
    ? ` · Evidence revision ${leadResult.evidence_revision}`
    : evidenceSources
      ? ` · ${evidenceSources.length} sources`
      : "";
  const contextLabel = leadResult
    ? leadResult.freshness === "stale"
      ? `Using older analysis${evidenceRevisionLabel}`
      : leadResult.freshness === "current"
        ? `Using current analysis${evidenceRevisionLabel}`
        : "Analysis freshness unavailable"
    : "Ask becomes available after Case analysis";

  const handleClose = () => {
    onToggleChat?.();
    window.requestAnimationFrame(() => {
      document.querySelector<HTMLButtonElement>('[aria-label="Open Ask"]')?.focus();
    });
  };

  return (
    <aside
      id="workspace-chat-panel"
      role="complementary"
      aria-label="Ask about this case"
      className="fixed inset-0 z-50 flex h-full w-full shrink-0 flex-col overflow-hidden border-l border-line bg-surface md:static md:z-auto md:w-[clamp(360px,34vw,480px)] md:max-w-[42vw]"
    >
      <div className="flex min-h-14 shrink-0 items-center border-b border-line bg-surface px-5 py-2.5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h2 className="text-sm font-bold text-ink">Ask about this case</h2>
            <p className="mt-1 text-[11px] leading-4 text-ink-muted">{contextLabel}</p>
          </div>
          <span
            className={`mt-2 h-2 w-2 shrink-0 rounded-full ${phase === "error"
              ? "bg-critical"
              : phase === "querying" || phase === "analyzing"
                ? "bg-evidence motion-safe:animate-pulse motion-reduce:animate-none"
                : phase === "awaiting_followup"
                  ? "bg-unresolved motion-safe:animate-ping"
                  : "bg-established"
            }`}
            title={`Status: ${phase}`}
          />
          {onToggleChat && (
            <button
              type="button"
              ref={closeButtonRef}
              onClick={handleClose}
              aria-label="Close Ask"
              title="Close Ask"
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-ink-muted transition-colors hover:bg-surface-hover hover:text-ink focus-visible:ring-2 focus-visible:ring-primary"
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
          chatStatus={chatStatus}
          phase={phase}
          hasAnalysisContext={hasAnalysisContext}
          leadResult={leadResult}
          evidenceSources={evidenceSources}
          onOpenOverview={() => onViewChange("overview")}
          onOpenIntake={() => onViewChange("intake")}
          onNavigateToSource={onNavigateToSource}
          onInputChange={onInputChange}
          onSubmit={onSubmit}
        />
      </div>
    </aside>
  );
}
