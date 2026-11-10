"use client";

import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { motionAllowed } from "@/lib/motion";
import { Icon } from "@/components/icons";
import type { WorkspaceView } from "@/lib/casePaths";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
import { useCaseChat } from "./useCaseChat";
import { useCaseAnalysis } from "@/features/analysis/queries";
import { toUserFacingError } from "@/lib/userFacingError";
import { ChatTranscript } from "./ChatTranscript";
import { useCaseSources } from "@/features/sources/queries";
import { gapTopic } from "@/features/analysis/overview";
import type { ChatMessageRead } from "@/lib/api/types";
import { hasThai } from "@/lib/language";

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

  const [wasOpen, setWasOpen] = useState(isOpen);
  const [leaving, setLeaving] = useState(false);
  if (wasOpen !== isOpen) {
    setWasOpen(isOpen);
    setLeaving(!isOpen && motionAllowed());
  }
  useEffect(() => {
    if (!leaving) return;
    const timer = window.setTimeout(() => setLeaving(false), 180);
    return () => window.clearTimeout(timer);
  }, [leaving]);

  if (!isOpen && !leaving) return null;

  const handleClose = () => {
    onCloseChat();
    window.requestAnimationFrame(() => {
      document.getElementById("ask-toggle")?.focus();
    });
  };

  const hasSources = Boolean(sources?.length);

  return (
    <aside
      id="workspace-chat-panel"
      role="complementary"
      aria-label="Ask about this case"
      aria-hidden={isOpen ? undefined : true}
      inert={isOpen ? undefined : true}
      className={`${isOpen ? "panel-in" : "panel-out"} fixed inset-0 z-50 flex h-full w-full shrink-0 flex-col overflow-hidden bg-surface text-ink md:static md:z-auto md:my-4 md:mr-4 md:h-auto md:w-[clamp(360px,30vw,420px)] md:rounded-[10px] md:shadow-[0_4px_24px_rgba(24,24,28,0.07)]`}
    >
      <div className="flex h-16 shrink-0 items-center justify-between border-b border-line pr-3 pl-6">
        <h2 className="text-lg font-semibold text-ink">Ask about this case</h2>
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
        <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-2.5 text-sm">
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
        pendingQuestionId={pendingQuestionId}
        onSuggest={(question) => {
          chat.changeInput(question);
          document.getElementById("chat-composer-input")?.focus();
        }}
      />

      <div className="shrink-0 border-t border-line px-4 pt-3 pb-4">
        <ChatComposer
          input={chat.input}
          isSubmitting={isSending}
          onInputChange={chat.changeInput}
          onSubmit={chat.submitMessage}
          placeholder={pendingQuestionId ? "Type your answer…" : "Ask about this case…"}
          answering={answeringQuestion(messages, pendingQuestionId)}
          onSkip={chat.submitContent}
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

function answeringQuestion(
  messages: ChatMessageRead[],
  pendingQuestionId: string | null,
): Answering | null {
  const question = messages.find((message) => message.id === pendingQuestionId);
  if (!question?.gap_key) return null;
  const number = messages.filter(
    (message) =>
      message.gap_key &&
      message.analysis_result_id === question.analysis_result_id &&
      message.ordinal <= question.ordinal,
  ).length;
  return {
    label: `question ${number}`,
    topic: gapTopic(question.gap_key, question.gap_key),
    unknown: hasThai(question.content) ? "ไม่ทราบ" : "I don't know",
  };
}

interface Answering {
  label: string;
  topic: string;
  unknown: string;
}

function ChatComposer({
  input,
  isSubmitting,
  onInputChange,
  onSubmit,
  placeholder,
  answering,
  onSkip,
}: {
  input: string;
  isSubmitting: boolean;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  placeholder: string;
  answering: Answering | null;
  onSkip: (answer: string) => void;
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
      <div className="overflow-hidden rounded-2xl border border-line-strong bg-surface shadow-[0_1px_3px_rgba(24,24,28,0.06)] transition-[border-color,box-shadow] focus-within:border-primary focus-within:shadow-[0_0_0_4px_var(--color-primary-soft)]">
        {answering && (
          <p className="flex items-center gap-1.5 border-b border-line bg-surface-nested px-4 py-2 text-xs">
            <span className="shrink-0 font-semibold text-primary">Answering {answering.label}</span>
            <span className="min-w-0 flex-1 truncate text-ink-muted">· {answering.topic}</span>
            <button
              type="button"
              disabled={isSubmitting}
              onClick={() => onSkip(answering.unknown)}
              title={`Answer "${answering.unknown}" and move on`}
              className="shrink-0 rounded-md px-2 py-0.5 font-semibold text-ink-secondary transition-colors hover:bg-surface-hover hover:text-ink disabled:cursor-not-allowed disabled:text-ink-disabled"
            >
              Don&apos;t know
            </button>
          </p>
        )}
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
          className="block max-h-[160px] min-h-12 w-full resize-none border-none bg-transparent px-4 pt-3 pb-1 text-base leading-6 text-ink shadow-none outline-none placeholder:text-ink-muted focus:ring-0 disabled:text-ink-disabled"
        />
        <div className="flex items-center justify-between gap-3 py-2 pr-2 pl-4">
          <span className="hidden text-xs text-ink-muted sm:inline">
            Enter to send · Shift+Enter for a new line
          </span>
          <button
            type="submit"
            disabled={isSubmitting || !input.trim() || isTooLong}
            aria-label="Send message"
            title="Send (Enter)"
            className="ml-auto flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-ivory transition-[background-color,transform] hover:bg-primary-hover active:scale-95 disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled"
          >
            <Icon name="send" className="h-4 w-4" />
          </button>
        </div>
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
