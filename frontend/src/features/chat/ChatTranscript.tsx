"use client";

import { useEffect, useRef } from "react";
import type { CaseAnalysisResultRead, CaseSourceRead, ChatMessageRead } from "@/lib/api/types";
import { Messages } from "./Messages";

interface ChatTranscriptProps {
  messages: ChatMessageRead[];
  isProcessing: boolean;
  isAnsweringQuestion?: boolean;
  leadResult?: CaseAnalysisResultRead | null;
  sources?: CaseSourceRead[] | null;
}

export function ChatTranscript({
  messages,
  isProcessing,
  isAnsweringQuestion = false,
  leadResult,
  sources,
}: ChatTranscriptProps) {
  const scrollerRef = useRef<HTMLDivElement | null>(null);

  const initialMessageIdsRef = useRef<Set<string> | null>(null);
  const leadResultIdRef = useRef<string | null>(leadResult?.id ?? null);

  useEffect(() => {
    if (leadResultIdRef.current !== (leadResult?.id ?? null)) {
      leadResultIdRef.current = leadResult?.id ?? null;
      initialMessageIdsRef.current =
        messages.length > 0 ? new Set(messages.map((message) => message.id)) : null;
      return;
    }
    if (!initialMessageIdsRef.current) {
      if (messages.length === 0) return;
      initialMessageIdsRef.current = new Set(messages.map((message) => message.id));
      return;
    }
    const hasNewMessage = messages.some(
      (message) => !initialMessageIdsRef.current?.has(message.id),
    );
    if (!hasNewMessage && !isProcessing) return;
    initialMessageIdsRef.current = new Set(messages.map((message) => message.id));
    const scroller = scrollerRef.current;
    scroller?.scrollTo?.({ top: scroller.scrollHeight, behavior: "smooth" });
  }, [isProcessing, leadResult?.id, messages]);

  return (
    <div ref={scrollerRef} className="relative min-h-0 flex-1 overflow-y-auto">
      {messages.length === 0 ? (
        <div className="flex h-full min-h-[320px] flex-col items-center justify-center px-8 text-center">
          <p className="max-w-60 text-sm leading-6 text-ink-muted">
            {leadResult
              ? "Ask about the findings, the sources, or what is still missing."
              : "Ask anything about this case."}
          </p>
        </div>
      ) : (
        <Messages
          messages={messages}
          isProcessing={isProcessing}
          isAnsweringQuestion={isAnsweringQuestion}
          sources={sources ?? []}
        />
      )}
    </div>
  );
}

export const SUGGESTION_LINES: Record<string, string> = {
  add_source: "ถ้าต้องการให้ข้อมูลนี้ถูกนำไปวิเคราะห์ ให้เพิ่มเป็น source ที่หน้า Sources",
  run_analysis: "กด Analyze เพื่อวิเคราะห์เคสอีกครั้ง",
};
