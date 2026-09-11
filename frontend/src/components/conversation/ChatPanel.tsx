import { useEffect, useRef, type FormEvent, type KeyboardEvent } from "react";
import type { CaseAnalysisResultRead, CaseEvidenceSnapshotRead, PersistedChatMessage, ThreadStatus } from "@/lib/api";
import type { RunPhase } from "@/components/common/types";
import { Icon } from "@/components/common/icons";
import { ChatTranscript } from "./ChatTranscript";

interface ChatPanelProps {
  messages: PersistedChatMessage[];
  input: string;
  threadStatus: ThreadStatus | null;
  phase: RunPhase;
  hasAnalysisContext: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  leadSnapshot?: CaseEvidenceSnapshotRead | null;
  onOpenOverview?: () => void;
  onOpenIntake?: () => void;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function ChatPanel({
  messages,
  input,
  threadStatus,
  phase,
  hasAnalysisContext,
  leadResult,
  leadSnapshot,
  onOpenOverview,
  onOpenIntake,
  onInputChange,
  onSubmit,
}: ChatPanelProps) {
  const isProcessing = phase === "querying" || phase === "analyzing";
  const isAwaitingClarification = threadStatus === "awaiting_followup";
  const isComposerDisabled = isProcessing || (!isAwaitingClarification && !hasAnalysisContext);

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden bg-canvas">
      <div className="min-h-0 flex-1 overflow-y-auto">
        <ChatTranscript
          messages={messages}
          isProcessing={isProcessing}
          leadResult={leadResult}
          leadSnapshot={leadSnapshot}
          onOpenOverview={onOpenOverview}
        />
      </div>

      <div className="shrink-0 border-t border-line bg-surface px-3.5 pb-3.5 pt-3 md:px-4 md:pb-4">
        <div className="mx-auto w-full max-w-4xl">
          {isAwaitingClarification ? (
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2 rounded-lg border border-unresolved/30 bg-unresolved/5 px-3 py-2 text-xs text-ink">
              <span className="font-semibold text-unresolved">Clarification needed</span>
              <span className="text-ink-secondary">Provide your answer below to resume the case analysis.</span>
            </div>
          ) : !hasAnalysisContext ? (
            <ChatBoundaryNotice
              message="Complete the Case analysis from Intake before using Chat. Chat will not start analysis."
              actionLabel="Open Case Intake"
              onAction={onOpenIntake}
            />
          ) : null}
          <ChatComposer
            input={input}
            isSubmitting={isComposerDisabled}
            onInputChange={onInputChange}
            onSubmit={onSubmit}
            placeholder={isAwaitingClarification ? "Type your answer to the clarification question…" : undefined}
          />
          <p className="mt-2 text-center text-[10px] leading-relaxed text-ink-muted">
            Press Ctrl+Enter or click Send to submit.
          </p>
        </div>
      </div>
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


interface ChatComposerProps {
  input: string;
  isSubmitting: boolean;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  placeholder?: string;
}

function ChatComposer({
  input,
  isSubmitting,
  onInputChange,
  onSubmit,
  placeholder,
}: ChatComposerProps) {
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
      <div className="relative flex items-center gap-2 rounded-2xl border border-line-strong bg-canvas py-2 pl-4 pr-2 shadow-[0_1px_3px_rgba(39,39,39,0.04)] transition-colors focus-within:border-primary focus-within:ring-1 focus-within:ring-primary">
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
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary text-ivory outline-none transition-[background-color,transform] hover:bg-charcoal-hover active:scale-95 active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled disabled:hover:scale-100"
        >
          <Icon name="send" className="h-3.5 w-3.5" />
        </button>
      </div>
    </form>
  );
}
