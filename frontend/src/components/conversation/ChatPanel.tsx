import { useEffect, useRef, type FormEvent, type KeyboardEvent } from "react";
import type {
  ChatMessageAction,
  PersistedChatMessage,
  ThreadStatus,
} from "@/lib/api";
import type { RunPhase } from "@/components/common/types";
import { Icon } from "@/components/common/icons";
import { ChatTranscript } from "./ChatTranscript";

interface ChatPanelProps {
  messages: PersistedChatMessage[];
  input: string;
  threadStatus: ThreadStatus | null;
  phase: RunPhase;
  postAnswerAction: ChatMessageAction | null;
  onInputChange: (value: string) => void;
  onPostAnswerActionChange: (action: ChatMessageAction) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

export function ChatPanel({
  messages,
  input,
  threadStatus,
  phase,
  postAnswerAction,
  onInputChange,
  onPostAnswerActionChange,
  onSubmit,
}: ChatPanelProps) {
  const isProcessing = phase === "querying" || phase === "analyzing";

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col overflow-hidden bg-canvas">
      {/* Transcript Scroll Area */}
      <div className="min-h-0 flex-1 overflow-y-auto">
        <ChatTranscript
          messages={messages}
          isProcessing={isProcessing}
        />
      </div>

      {/* Input Area */}
      <div className="shrink-0 bg-canvas px-4 pt-1 pb-3 sm:px-6 sm:pb-4">
        <div className="mx-auto w-full max-w-3xl">
          {threadStatus === "answered" && (
            <div className="mb-2 flex items-center gap-1.5 px-1">
              <span className="text-[10px] font-bold text-ink-secondary">
                Next action:
              </span>
              <button
                type="button"
                onClick={() => onPostAnswerActionChange("ask")}
                className={`rounded-full border px-2.5 py-0.5 text-[11px] font-bold transition-all cursor-pointer ${
                  postAnswerAction === "ask"
                    ? "border-primary bg-primary text-ivory shadow-sm"
                    : "border-line-strong bg-surface text-ink-secondary hover:border-primary hover:bg-surface-hover"
                }`}
              >
                Ask question
              </button>
              <button
                type="button"
                onClick={() => onPostAnswerActionChange("add_case_info")}
                className={`rounded-full border px-2.5 py-0.5 text-[11px] font-bold transition-all cursor-pointer ${
                  postAnswerAction === "add_case_info"
                    ? "border-primary bg-primary text-ivory shadow-sm"
                    : "border-line-strong bg-surface text-ink-secondary hover:border-primary hover:bg-surface-hover"
                }`}
              >
                Add case info
              </button>
            </div>
          )}
          <ChatComposer
            input={input}
            isSubmitting={isProcessing}
            onInputChange={onInputChange}
            onSubmit={onSubmit}
          />
          <p className="mt-1.5 text-center text-[9.5px] text-ink-muted">
            CyberCase maps security events to MITRE ATT&amp;CK intelligence.
          </p>
        </div>
      </div>
    </div>
  );
}

interface ChatComposerProps {
  input: string;
  isSubmitting: boolean;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

function ChatComposer({
  input,
  isSubmitting,
  onInputChange,
  onSubmit,
}: ChatComposerProps) {
  const formRef = useRef<HTMLFormElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(Math.max(textarea.scrollHeight, 22), 160)}px`;
  }, [input]);

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      formRef.current?.requestSubmit();
    }
  };

  return (
    <form ref={formRef} onSubmit={onSubmit} className="relative w-full">
      <div className="relative flex items-center gap-2 rounded-2xl border border-line-strong bg-surface py-1.5 pl-3.5 pr-1.5 shadow-[0_1px_4px_rgba(39,39,39,0.05)] transition-all focus-within:border-primary focus-within:ring-1 focus-within:ring-primary">
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
          placeholder="Message CyberCase or paste incident logs..."
          className="max-h-[160px] min-h-[22px] flex-1 resize-none border-none bg-transparent py-0.5 text-xs sm:text-sm leading-snug text-ink outline-none shadow-none placeholder:text-ink-muted focus:border-none focus:outline-none focus:ring-0 focus-visible:border-none focus-visible:outline-none focus-visible:ring-0 disabled:text-ink-disabled"
        />

        <button
          type="submit"
          disabled={isSubmitting || !input.trim()}
          aria-label="Send message"
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-xl bg-primary text-ivory outline-none transition-all hover:scale-105 hover:bg-charcoal-hover active:scale-95 active:bg-charcoal-pressed focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-control-disabled disabled:text-ink-disabled disabled:hover:scale-100"
        >
          <Icon name="send" className="h-3.5 w-3.5" />
        </button>
      </div>
    </form>
  );
}
