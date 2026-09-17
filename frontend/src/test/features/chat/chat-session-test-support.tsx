import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { vi } from "vitest";
import type { CaseChatDetail, CaseChatMessageResult, CaseChatStatus, CaseRead, ChatMessageRead } from "@/lib/api";
import { useCaseChat } from "@/features/chat/useCaseChat";

export function message(caseId: string, ordinal: number, role: "user" | "assistant", content: string = role): ChatMessageRead {
  return {
    id: `${caseId}-${ordinal}`, case_id: caseId, ordinal, role, content,
    message_kind: "conversation", analysis_result_id: null,
    metadata_json: {}, retrieval_context_id: null, created_at: "2026-09-05T00:00:00Z",
  };
}

export function caseChat(caseId = "a", status: CaseChatStatus = "idle", messages: ChatMessageRead[] = []): CaseChatDetail {
  return {
    case_id: caseId, status, messages,
  };
}

export function caseRecord(id = "a", status: CaseChatStatus = "idle"): CaseRead {
  return {
    id,
    title: "Saved case",
    status,
    evidence_revision: 1,
    processing_status: "idle",
    has_pending_followup: status === "awaiting_followup",
    analysis_freshness: "current",
    created_at: "2026-09-05T00:00:00Z",
    updated_at: "2026-09-05T00:00:00Z",
  };
}

export function caseAccepted(
  request: ChatMessageRead,
): CaseChatMessageResult {
  return {
    message: request,
    run: {
      id: "run-1",
      case_id: request.case_id,
      evidence_revision: 1,
      status: "running",
      attempt_count: 0,
      error_code: null,
      error_message: null,
      created_at: request.created_at,
      started_at: null,
      finished_at: null,
      updated_at: request.created_at,
    },
  };
}

export function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

export function renderSession(nativeCaseId: string | null = null) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
  const upsert = vi.fn();
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  const hook = renderHook(() => {
    const chat = useCaseChat({
      caseId: nativeCaseId,
      cases: [caseRecord("a"), caseRecord("b")],
      upsertCase: upsert,
      isChatOpen: true,
    });
    return chat;
  }, { wrapper });
  return { ...hook, queryClient, upsert };
}

export async function tick(milliseconds = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(milliseconds); });
}
