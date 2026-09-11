import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { vi } from "vitest";
import type { CaseChatMessageAccepted, CaseRead, ChatThreadDetail, PersistedChatMessage, ThreadStatus } from "@/lib/api";
import { useChatThreadSelection } from "@/features/chat/workspace/use-chat-thread-selection";
import { useChatSubmission } from "@/features/chat/runs/useChatSubmission";

export function message(threadId: string, ordinal: number, role: "user" | "assistant", content: string = role): PersistedChatMessage {
  return {
    id: `${threadId}-${ordinal}`, thread_id: threadId, ordinal, role, content,
    metadata_json: {}, retrieval_context_id: null, created_at: "2026-09-05T00:00:00Z",
  };
}

export function thread(id = "a", status: ThreadStatus = "idle", messages: PersistedChatMessage[] = []): ChatThreadDetail {
  return {
    id, title: "Saved case", status, messages,
    created_at: "2026-09-05T00:00:00Z", updated_at: "2026-09-05T00:00:00Z",
  };
}

export function caseRecord(id = "a", status: ThreadStatus = "idle"): CaseRead {
  return {
    id,
    title: "Saved case",
    status,
    chat_thread_id: id,
    created_at: "2026-09-05T00:00:00Z",
    updated_at: "2026-09-05T00:00:00Z",
  };
}

export function caseAccepted(
  request: PersistedChatMessage,
  operation: "analysis" | "ask" = "analysis",
): CaseChatMessageAccepted {
  return {
    message: request,
    run: {
      id: "run-1", case_id: request.thread_id, operation,
      snapshot_id: "snapshot-1", request_message_id: request.id,
      context_analysis_result_id: operation === "ask" ? "result-1" : null,
      clarification_id: null, status: "running", attempt_count: 0,
      error_code: null, error_message: null, created_at: request.created_at,
      started_at: null, finished_at: null, updated_at: request.created_at,
    },
  };
}

export function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

export function renderSession(nativeCaseId: string | null = "a") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
  const upsert = vi.fn();
  const updateCase = vi.fn().mockResolvedValue(caseRecord());
  const wrapper = ({ children }: { children: ReactNode }) =>
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  const hook = renderHook(() => {
    const session = useChatThreadSelection({ cacheUpsertThread: upsert });
    const submission = useChatSubmission({
      session,
      cases: [caseRecord("a"), caseRecord("b")],
      upsertCase: upsert,
      updateCase,
      caseId: nativeCaseId,
    });
    return { session, ...submission };
  }, { wrapper });
  return { ...hook, queryClient, upsert };
}

export async function tick(milliseconds = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(milliseconds); });
}
