import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, renderHook } from "@testing-library/react";
import { useState, type ReactNode } from "react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { useChatThreadSelection } from "@/features/chat/workspace/use-chat-thread-selection";
import { useChatThreadDeletion } from "@/features/chat/workspace/use-chat-thread-deletion";
import { deferred, thread, tick } from "./chat-session-test-support";

beforeEach(() => {
  vi.useFakeTimers();
  vi.spyOn(api, "getChatThread").mockImplementation(async (id) => thread(id));
});
afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); });

function renderDeletion(deleteThread: (id: string) => Promise<void>) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } });
  const upsert = vi.fn();
  const router = { replace: vi.fn() };
  const wrapper = ({ children }: { children: ReactNode }) =>
    <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  const hook = renderHook(() => {
    const session = useChatThreadSelection({ cacheUpsertThread: upsert });
    const [candidate, setCandidate] = useState<api.ChatThreadRead | null>(thread("a"));
    const deletion = useChatThreadDeletion({
      session, deleteCandidate: candidate, setDeleteCandidate: setCandidate,
      deletingThreadId: null, activeView: "overview", threads: [thread("a"), thread("b")],
      deleteThread, router,
    });
    return { session, deletion };
  }, { wrapper });
  return { ...hook, router };
}

it("selects the remaining case after deleting the active case", async () => {
  const remove = vi.fn().mockResolvedValue(undefined);
  const { result, router } = renderDeletion(remove);
  await act(async () => { await result.current.session.selectThread("a"); });
  await tick();
  await act(async () => { await result.current.deletion.confirmDelete(); });
  await tick();
  expect(remove).toHaveBeenCalledWith("a");
  expect(result.current.session.activeThreadId).toBe("b");
  expect(router.replace).toHaveBeenCalledWith("/chat/b/overview");
});

it("restores the active case after a failed deletion", async () => {
  const { result, router } = renderDeletion(vi.fn().mockRejectedValue(new Error("Delete failed")));
  await act(async () => { await result.current.session.selectThread("a"); });
  await tick();
  await act(async () => { await result.current.deletion.confirmDelete(); });
  await tick();
  expect(result.current.session.getActiveThreadId()).toBe("a");
  expect(result.current.session.threadStatus).toBe("idle");
  expect(router.replace).not.toHaveBeenCalled();
});

it("does not override a newer selection when an earlier deletion completes", async () => {
  const waiting = deferred<void>();
  const { result, router } = renderDeletion(() => waiting.promise);
  await act(async () => { await result.current.session.selectThread("a"); });
  await tick();
  let deleted!: Promise<void>;
  act(() => { deleted = result.current.deletion.confirmDelete(); });
  await act(async () => { await result.current.session.selectThread("b"); });
  await tick();
  await act(async () => { waiting.resolve(); await deleted; });
  expect(result.current.session.getActiveThreadId()).toBe("b");
  expect(router.replace).not.toHaveBeenCalled();
});
