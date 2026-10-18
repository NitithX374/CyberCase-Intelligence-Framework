"use client";

import type { CaseSourceRead, ChatMessageRead } from "@/lib/api/types";
import { parseCaseSources } from "@/features/citations/sourceRefs";
import { chatFollowups } from "@/features/citations/followupSources";
import { Markdown } from "@/components/Markdown";
import { stripInlineCitations } from "./inlineCitations";
import { AnswerUnits } from "./AnswerUnits";
import { SuggestionLine } from "./SuggestionLine";
import { claimItem, sourceReferences } from "./chatReferences";
import { AnswerReferences } from "./AnswerReferences";

export function Messages({
  messages,
  isProcessing,
  isAnsweringQuestion,
  sources,
}: {
  messages: ChatMessageRead[];
  isProcessing: boolean;
  isAnsweringQuestion: boolean;
  sources: CaseSourceRead[];
}) {
  const citable = parseCaseSources(sources, chatFollowups(messages));
  return (
    <div className="space-y-6 px-5 py-6">
      {messages.map((message) => {
        const isUser = message.role === "user";
        const isQuestion = Boolean(message.gap_key);

        if (isUser) {
          return (
            <article key={message.id} className="flex justify-end">
              <p className="max-w-[88%] rounded-2xl rounded-br-md bg-surface-nested px-4 py-2.5 text-[15px] leading-7 whitespace-pre-wrap text-ink [overflow-wrap:anywhere]">
                {message.content}
              </p>
            </article>
          );
        }

        if (isQuestion) {
          return (
            <article key={message.id}>
              <p className="mb-1 text-xs font-medium text-ink-muted">Question</p>
              <Markdown content={message.content} />
            </article>
          );
        }

        const units = message.metadata_json.answer_units ?? [];
        const claims = message.metadata_json.analysis_trace?.claims ?? [];
        return (
          <article key={message.id}>
            {units.length > 0 ? (
              <AnswerUnits units={units} claims={claims} sources={citable} />
            ) : (
              <>
                <Markdown content={stripInlineCitations(message.content)} />
                <AnswerReferences {...sourceReferences(claims.map(claimItem), citable)} />
              </>
            )}
            <SuggestionLine suggestion={message.metadata_json.suggestion} />
          </article>
        );
      })}

      {isProcessing && (
        <p role="status" className="text-[13px] text-ink-muted">
          {isAnsweringQuestion ? "Updating the analysis with your answer…" : "Answering…"}
        </p>
      )}
    </div>
  );
}
