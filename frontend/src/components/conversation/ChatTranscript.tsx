"use client";

import { useEffect, useRef } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import {
  followUpGapDetailForMessage,
} from "@/lib/chat-followup";
import { mitreCandidatesForMessage } from "@/lib/mitre-candidate";
import { Icon } from "@/components/common/icons";
import { StatusPill } from "@/components/common/StatusPill";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";
import { AnalysisEvidenceReferences } from "./AnalysisEvidenceReferences";
import { FollowUpActionCard } from "./FollowUpActionCard";
import { MitreCandidatePanel } from "./MitreCandidatePanel";

interface ChatTranscriptProps {
  messages: PersistedChatMessage[];
  isProcessing: boolean;
}

export function ChatTranscript({ messages, isProcessing }: ChatTranscriptProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView?.({ behavior: "smooth" });
  }, [messages.length, isProcessing]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-8 text-center">
        <div className="workspace-card max-w-md space-y-3 p-8">
          <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-surface-nested text-ink-secondary">
            <Icon name="chat" className="h-5 w-5" />
          </div>
          <h3 className="text-base font-extrabold tracking-tight text-ink">Case Discussion</h3>
          <p className="text-xs leading-relaxed text-ink-secondary">
            Ask about the current case analysis or add information that should become part of the case material.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl space-y-1 px-4 py-4 md:px-5 md:py-6">
      {messages.map((message) => {
        const isUser = message.role === "user";
        const followUpGap = followUpGapDetailForMessage(message);
        const mitreCandidates = isUser ? null : mitreCandidatesForMessage(message);
        return (
          <article key={message.id} className="border-b border-line py-5 first:pt-1 last:border-b-0">
            <header className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.1em] text-ink-muted">
              <span className={isUser ? "text-ink" : "text-accent"}>
                {isUser ? "Submitted material" : "CyberCase analysis"}
              </span>
            </header>

            <div
              className={`mt-3 ${
                isUser
                  ? "ml-auto max-w-[90%] rounded-xl bg-primary px-4 py-3 text-ivory sm:max-w-[78%] sm:px-5"
                  : "border-l-2 border-line-strong pl-4 pr-1 sm:pl-5"
              }`}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
              ) : (
                <>
                  <ChatMessageMarkdown content={message.content} />
                  <AnalysisEvidenceReferences
                    analysisMessage={message}
                    messages={messages}
                  />
                  {followUpGap && <FollowUpActionCard detail={followUpGap} />}
                  {mitreCandidates && <MitreCandidatePanel candidates={mitreCandidates} />}
                </>
              )}
            </div>
          </article>
        );
      })}

      {isProcessing && (
        <div className="flex items-center gap-2 px-1 py-5 text-xs font-semibold text-ink-secondary">
          <StatusPill tone="evidence">Analysis in progress</StatusPill>
          <span>Reviewing the current case material…</span>
        </div>
      )}

      <div ref={bottomRef} aria-hidden="true" />
    </div>
  );
}
