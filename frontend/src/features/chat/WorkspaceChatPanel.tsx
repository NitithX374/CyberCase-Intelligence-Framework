"use client";

import { useEffect, useRef, type FormEvent, type KeyboardEvent } from "react";
import { Icon } from "@/components/icons";
import type { WorkspaceView } from "@/lib/casePaths";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
import { useCaseChat } from "./useCaseChat";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { toUserFacingError } from "@/lib/userFacingError";
import { ChatTranscript } from "./ChatTranscript";
import { useCaseSources } from "@/features/sources/queries";

interface WorkspaceChatPanelProps {
  caseId: string | null;
  isOpen: boolean;
  onOpenChat: () => void;
  onCloseChat: () => void;
  onViewChange: (view: WorkspaceView) => void;
}

export function WorkspaceChatPanel({
  caseId,
  isOpen,
  onOpenChat,
  onCloseChat,
  onViewChange,
}: WorkspaceChatPanelProps) {
  const chat = useCaseChat({ caseId });
  const analysisQuery = useCaseAnalysis(caseId);
  const sourcesQuery = useCaseSources(caseId);
  const sources = sourcesQuery.data ?? null;
  const sourcesFailed = sourcesQuery.isLoadingError;

  const leadResult = analysisQuery.data ?? null;
  const messages = chat.messages;
  const isSending = chat.isSending;
  const isAnsweringQuestion = chat.isAnsweringQuestion;

  const pendingQuestionId = chat.pendingQuestionId;
  const announcedQuestionRef = useRef<string | null>(null);
  useEffect(() => {
    if (!pendingQuestionId || announcedQuestionRef.current === pendingQuestionId) return;
    announcedQuestionRef.current = pendingQuestionId;
    onOpenChat();
  }, [pendingQuestionId, onOpenChat]);

  if (!isOpen) return null;

  const handleClose = () => {
    onCloseChat();
    window.requestAnimationFrame(() => {
      document.querySelector<HTMLButtonElement>('[aria-label="Open Ask"]')?.focus();
    });
  };

  const hasSources = Boolean(sources?.length);

  return (
    <aside
      id="workspace-chat-panel"
      role="complementary"
      aria-label="Ask about this case"
      className="fixed inset-0 z-50 flex h-full w-full shrink-0 flex-col overflow-hidden bg-surface md:static md:z-auto md:w-[clamp(340px,32vw,440px)] md:border-l md:border-line"
    >
      <div className="flex h-14 shrink-0 items-center justify-between border-b border-line pr-3 pl-5">
        <h2 className="text-[15px] font-semibold text-ink">Ask</h2>
        <button
          type="button"
          onClick={handleClose}
          aria-label="Close Ask"
          title="Close"
          className="icon-btn"
        >
          <Icon name="close" className="h-5 w-5" />
        </button>
      </div>

      {messages.length === 0 && !hasSources && !sourcesFailed && (
        <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-2.5 text-[13px]">
          <p className="text-ink-muted">This case has no sources yet.</p>
          <button
            type="button"
            onClick={() => onViewChange("sources")}
            className="shrink-0 font-semibold text-ink hover:underline"
          >
            Add sources
          </button>
        </div>
      )}

      <ChatTranscript
        messages={messages}
        isProcessing={isSending}
        isAnsweringQuestion={isAnsweringQuestion}
        leadResult={leadResult}
        sources={sources}
      />

      <div className="shrink-0 px-4 pt-2 pb-4">
        <ChatComposer
          input={chat.input}
          isSubmitting={isSending}
          onInputChange={chat.changeInput}
          onSubmit={chat.submitMessage}
          placeholder={pendingQuestionId ? "Type your answer…" : "Ask about this case…"}
        />
      </div>

      <MeaningfulErrorModal
        isOpen={Boolean(chat.queryError)}
        error={chat.queryError ? toUserFacingError(chat.queryError) : null}
        onClose={chat.clearQueryError}
        onRetry={chat.retryQuery}
      />
    </aside>
  );
}

const MESSAGE_MAX_LENGTH = 4_000;

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
  placeholder: string;
}) {
  const formRef = useRef<HTMLFormElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const isTooLong = input.length > MESSAGE_MAX_LENGTH;

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(Math.max(textarea.scrollHeight, 24), 160)}px`;
  }, [input]);

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== "Enter" || event.shiftKey || event.nativeEvent.isComposing) return;
    event.preventDefault();
    if (!input.trim() || isTooLong) return;
    formRef.current?.requestSubmit();
  };

  return (
    <form ref={formRef} onSubmit={onSubmit} className="relative w-full">
      <div className="flex items-end gap-2 rounded-xl border border-line-strong bg-surface py-2 pr-2 pl-3.5 transition-colors focus-within:border-ink">
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
          placeholder={placeholder}
          className="max-h-[160px] min-h-6 flex-1 resize-none self-center border-none bg-transparent py-1 text-[15px] leading-6 text-ink shadow-none outline-none placeholder:text-ink-muted focus:ring-0 disabled:text-ink-disabled"
        />
        <button
          type="submit"
          disabled={isSubmitting || !input.trim() || isTooLong}
          aria-label="Send message"
          title="Send (Enter)"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-ivory transition-colors hover:bg-charcoal-hover disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled"
        >
          <Icon name="send" className="h-4 w-4" />
        </button>
      </div>
      {isTooLong && (
        <p role="status" className="mt-1.5 px-1 text-xs text-ink-muted">
          {input.length.toLocaleString("en-US")} of {MESSAGE_MAX_LENGTH.toLocaleString("en-US")}{" "}
          characters. Shorten the message or send it in parts.
        </p>
      )}
    </form>
  );
}
