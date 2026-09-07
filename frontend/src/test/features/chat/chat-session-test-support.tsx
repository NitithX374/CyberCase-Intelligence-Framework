import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { vi } from "vitest";
import type { ChatMessageAccepted, ChatThreadDetail, PersistedChatMessage, ThreadStatus } from "@/lib/api";
import { useChatThreadSelection } from "@/features/chat/workspace/use-chat-thread-selection";
import { useChatSubmission } from "@/features/chat/runs/use-chat-submission";
import { chatPath } from "@/features/chat/routing/chat-route";

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

export function accepted(request: PersistedChatMessage): ChatMessageAccepted {
  return {
    message: request,
    run: {
      id: "run-1", thread_id: request.thread_id, request_message_id: request.id,
      status: "running", error_code: null, error_message: null,
      created_at: request.created_at, updated_at: request.created_at,
    },
  };
}

export function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (error: unknown) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

export function renderSession() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
  const upsert = vi.fn();
  const router = { push: vi.fn() };
  const createThread = vi.fn().mockResolvedValue(thread("new"));
  const updateThread = vi.fn().mockResolvedValue(thread());
  const wrapper = ({ children }: { children: ReactNode }) =>
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  const hook = renderHook(() => {
    const session = useChatThreadSelection({ cacheUpsertThread: upsert });
    const submission = useChatSubmission({
      session, threads: [thread("a"), thread("b")], createThread, updateThread, router, chatPath,
    });
    return { session, ...submission };
  }, { wrapper });
  return { ...hook, queryClient, upsert, router, createThread };
}

export async function tick(milliseconds = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(milliseconds); });
}
