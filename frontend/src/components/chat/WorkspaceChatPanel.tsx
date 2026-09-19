"use client";

import { useEffect, useRef, type FormEvent, type KeyboardEvent } from "react";
import { Icon } from "@/components/common/icons";
import type { CaseAnalysisResultRead, CaseSourceRead, ChatMessageRead } from "@/lib/api";
import type { WorkspaceView } from "@/components/common/types";
import { ChatTranscript } from "./ChatTranscript";

interface WorkspaceChatPanelProps {
  isOpen: boolean;
  isSending: boolean;
  messages: ChatMessageRead[];
  isAnsweringQuestion?: boolean;
  input: string;
  hasAnalysisContext: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  sources?: CaseSourceRead[] | null;
  onViewChange: (view: WorkspaceView) => void;
  onNavigateToSource?: (messageId: string) => void;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onToggleChat?: () => void;
}

export function WorkspaceChatPanel({
  isOpen,
  isSending,
  messages,
  isAnsweringQuestion = false,
  input,
  hasAnalysisContext,
  leadResult,
  sources,
  onViewChange,
  onNavigateToSource,
  onInputChange,
  onSubmit,
  onToggleChat,
}: WorkspaceChatPanelProps) {
  const closeButtonRef = useRef<HTMLButtonElement | null>(null);

  if (!isOpen) return null;

  const sourceRevisionLabel = leadResult
    ? ` · Source revision ${leadResult.source_revision}`
    : sources
      ? ` · ${sources.length} sources`
      : "";
  const contextLabel = leadResult
    ? leadResult.freshness === "stale"
      ? `Using older analysis${sourceRevisionLabel}`
      : leadResult.freshness === "current"
        ? `Using current analysis${sourceRevisionLabel}`
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
            className={`mt-2 h-2 w-2 shrink-0 rounded-full ${
              isSending
                ? "bg-accent motion-safe:animate-pulse motion-reduce:animate-none"
                : "bg-established"
            }`}
            title={isSending ? "Answering" : "Ready"}
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
            <EmptyChatSourcesNotice onOpenSources={() => onViewChange("sources")} />
          </div>
        )}
        <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden bg-surface">
          <div className="min-h-0 flex-1 overflow-y-auto">
            <ChatTranscript
              messages={messages}
              isProcessing={isSending}
              isAnsweringQuestion={isAnsweringQuestion}
              leadResult={leadResult}
              sources={sources}
              onNavigateToSource={onNavigateToSource}
            />
          </div>

          <div className="shrink-0 border-t border-line bg-surface px-3.5 pb-3.5 pt-3 md:px-4 md:pb-4">
            <div className="mx-auto w-full max-w-4xl">
              {!hasAnalysisContext && (
                <ChatBoundaryNotice
                  message="Run the Case analysis from the sources page before using Chat. Chat will not start analysis."
                  actionLabel="Open case sources"
                  onAction={() => onViewChange("sources")}
                />
              )}
              <ChatComposer
                input={input}
                isSubmitting={isSending || !hasAnalysisContext}
                onInputChange={onInputChange}
                onSubmit={onSubmit}
              />
              <p className="mt-2 text-center text-[10px] leading-relaxed text-ink-muted">
                Ctrl+Enter to send.
              </p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}

function EmptyChatSourcesNotice({ onOpenSources }: { onOpenSources: () => void }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-line bg-surface px-4 py-3 text-xs text-ink-secondary">
      <p className="truncate">
        ยังไม่ได้บันทึกรายละเอียดสำนวนคดี — เริ่มที่หน้า Sources เพื่อให้ระบบจัดทำภาพรวมคดี
      </p>
      <button
        type="button"
        onClick={onOpenSources}
        className="shrink-0 text-[11px] font-bold text-ink hover:text-accent hover:underline"
      >
        เปิดหน้า Sources →
      </button>
    </div>
  );
}

function ChatBoundaryNotice({
  message,
  actionLabel,
  onAction,
}: {
  message: string;
  actionLabel: string;
  onAction?: () => void;
}) {
  return (
    <div className="mb-3 flex flex-wrap items-center justify-between gap-2 px-1 text-[11px] text-ink-secondary">
      <span>{message}</span>
      {onAction && (
        <button
          type="button"
          onClick={onAction}
          className="font-bold text-ink underline decoration-line underline-offset-2 hover:text-accent"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

function ChatComposer({
  input,
  isSubmitting,
  onInputChange,
  onSubmit,
  placeholder,
}: {
  input: string;
  isSubmitting: boolean;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  placeholder?: string;
}) {
  const formRef = useRef<HTMLFormElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(Math.max(textarea.scrollHeight, 24), 160)}px`;
  }, [input]);

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      formRef.current?.requestSubmit();
    }
  };

  return (
    <form ref={formRef} onSubmit={onSubmit} className="relative w-full">
      <div className="relative flex items-center gap-2 rounded-md border border-line-strong bg-surface py-2 pl-3 pr-2 transition-colors focus-within:border-primary focus-within:ring-1 focus-within:ring-primary">
        <label htmlFor="chat-composer-input" className="sr-only">
          Chat message
        </label>
        <textarea
          ref={textareaRef}
          id="chat-composer-input"
          rows={1}
          value={input}
          disabled={isSubmitting}
          onKeyDown={handleKeyDown}
          onChange={(event) => onInputChange(event.target.value)}
          placeholder={placeholder ?? "Ask a question about the completed Case analysis…"}
          className="max-h-[160px] min-h-6 flex-1 resize-none border-none bg-transparent py-0.5 text-xs leading-snug text-ink outline-none shadow-none placeholder:text-ink-muted focus:border-none focus:outline-none focus:ring-0 focus-visible:border-none focus-visible:outline-none focus-visible:ring-0 disabled:text-ink-disabled sm:text-sm"
        />
        <button
          type="submit"
          disabled={isSubmitting || !input.trim()}
          aria-label="Send message"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary text-ivory outline-none transition-[background-color,transform] hover:bg-charcoal-hover active:scale-95 active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled disabled:hover:scale-100"
        >
          <Icon name="send" className="h-3.5 w-3.5" />
        </button>
      </div>
    </form>
  );
}
