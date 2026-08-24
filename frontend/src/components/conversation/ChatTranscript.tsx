"use client";

import { useEffect, useRef } from "react";
import type { PersistedChatMessage } from "@/lib/api";
import {
  followUpGapDetailForMessage,
  type ChatFollowUpGapDetail,
} from "@/lib/chat-followup";
import { mitreCandidatesForMessage } from "@/lib/mitre-candidate";
import { ChatMessageMarkdown } from "./ChatMessageMarkdown";
import { MitreCandidatePanel } from "./MitreCandidatePanel";

interface ChatTranscriptProps {
  messages: PersistedChatMessage[];
  isProcessing: boolean;
}

export function ChatTranscript({
  messages,
  isProcessing,
}: ChatTranscriptProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, isProcessing]);

  if (messages.length === 0) {
    return (
      <div className="flex h-full min-h-[400px] flex-col items-center justify-center p-8 text-center">
        <div className="mx-auto max-w-md">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-hover text-lg font-black text-ink">
            CC
          </div>
          <h3 className="mt-4 text-base font-extrabold text-ink">
            Investigation Console
          </h3>
          <p className="mt-2 text-xs leading-relaxed text-ink-secondary">
            Describe an incident, paste security logs, or ask about threat techniques.
            CyberCase will analyze the details and identify relevant MITRE ATT&amp;CK tactics.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6 px-4 py-6 sm:px-6">
      {messages.map((message) => {
        const isUser = message.role === "user";
        const followUpGap = followUpGapDetailForMessage(message);
        const mitreCandidates = isUser ? null : mitreCandidatesForMessage(message);
        return (
          <div
            key={message.id}
            className={`flex flex-col ${isUser ? "items-end" : "items-start w-full"}`}
          >
            <div className="flex items-center gap-2 mb-1.5 px-1">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-ink-secondary">
                {isUser ? "Analyst" : "CyberCase AI"}
              </span>
              <span className="text-[10px] text-ink-secondary">
                #{message.ordinal}
              </span>
            </div>

            <div
              className={`rounded-2xl px-4 py-3.5 shadow-[0_1px_3px_rgba(39,39,39,0.04)] sm:px-5 sm:py-4 ${
                isUser
                  ? "max-w-[85%] bg-primary text-ivory"
                  : "w-full border border-line bg-surface text-ink"
              }`}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {message.content}
                </p>
              ) : (
                <>
                  <ChatMessageMarkdown content={message.content} />
                  {followUpGap && <FollowUpExplanation detail={followUpGap} />}
                  {mitreCandidates && (
                    <MitreCandidatePanel candidates={mitreCandidates} />
                  )}
                </>
              )}
            </div>
          </div>
        );
      })}

      {isProcessing && (
        <div className="flex items-center gap-3 px-2 text-xs font-semibold text-ink-secondary">
          <span className="flex h-2 w-2 rounded-full bg-primary animate-ping" />
          <span>Analyzing incident details &amp; mapping MITRE intelligence...</span>
        </div>
      )}

      <div ref={bottomRef} aria-hidden="true" />
    </div>
  );
}

function FollowUpExplanation({ detail }: { detail: ChatFollowUpGapDetail }) {
  return (
    <details className="mt-3 rounded-xl border border-line bg-surface-hover px-3.5 py-3 text-ink">
      <summary className="cursor-pointer text-xs font-extrabold text-ink marker:text-ink-secondary">
        Why is CyberCase asking this?
      </summary>
      <dl className="mt-3 grid gap-3 border-t border-line pt-3 text-xs leading-5">
        <div>
          <dt className="font-extrabold text-ink">Missing information</dt>
          <dd className="mt-0.5 text-ink-secondary">{detail.topic}</dd>
          <dd className="mt-0.5 text-ink-secondary">{detail.description}</dd>
        </div>
        <div>
          <dt className="font-extrabold text-ink">Why it matters</dt>
          <dd className="mt-0.5 text-ink-secondary">{detail.reason}</dd>
        </div>
        <div>
          <dt className="font-extrabold text-ink">Affected conclusion</dt>
          <dd className="mt-0.5 text-ink-secondary">{detail.affects}</dd>
        </div>
        <div className="flex items-center gap-2">
          <dt className="font-extrabold text-ink">Priority</dt>
          <dd className="rounded-full border border-line-strong bg-surface px-2 py-0.5 font-bold capitalize text-ink-secondary">
            {detail.priority}
          </dd>
        </div>
      </dl>
    </details>
  );
}
