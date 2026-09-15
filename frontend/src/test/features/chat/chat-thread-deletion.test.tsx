import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, renderHook } from "@testing-library/react";
import { useState, type ReactNode } from "react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { useCaseChatSelection } from "@/features/chat/workspace/use-case-chat-selection";
import { useCaseDeletion } from "@/features/chat/workspace/use-case-deletion";
import { caseRecord, deferred, caseChat, tick } from "./chat-session-test-support";

beforeEach(() => {
  vi.useFakeTimers();
  vi.spyOn(api, "getCaseChat").mockImplementation(async (id) => caseChat(id));
});
afterEach(() => { cleanup(); vi.useRealTimers(); vi.restoreAllMocks(); });

function renderDeletion(deleteThread: (id: string) => Promise<void>) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity } } });
  const upsert = vi.fn();
  const router = { replace: vi.fn() };
  const wrapper = ({ children }: { children: ReactNode }) =>
    <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  const hook = renderHook(() => {
    const session = useCaseChatSelection({ cacheUpsertCaseChat: upsert });
    const [candidate, setCandidate] = useState<api.CaseRead | null>(caseRecord("a"));
    const deletion = useCaseDeletion({
      session, deleteCandidate: candidate, setDeleteCandidate: setCandidate,
      deletingCaseId: null, activeView: "overview",
      cases: [caseRecord("a"), caseRecord("b")],
      deleteCase: deleteThread, router,
    });
    return { session, deletion };
  }, { wrapper });
  return { ...hook, router };
}

it("selects the remaining case after deleting the active case", async () => {
  const remove = vi.fn().mockResolvedValue(undefined);
  const { result, router } = renderDeletion(remove);
  await act(async () => { await result.current.session.selectCaseChat("a"); });
  await tick();
  await act(async () => { await result.current.deletion.confirmDelete(); });
  await tick();
  expect(remove).toHaveBeenCalledWith("a");
  expect(result.current.session.activeCaseChatId).toBe("b");
  expect(router.replace).toHaveBeenCalledWith("/case/b/overview");
});

it("restores the active case after a failed deletion", async () => {
  const { result, router } = renderDeletion(vi.fn().mockRejectedValue(new Error("Delete failed")));
  await act(async () => { await result.current.session.selectCaseChat("a"); });
  await tick();
  await act(async () => { await result.current.deletion.confirmDelete(); });
  await tick();
  expect(result.current.session.getActiveCaseChatId()).toBe("a");
  expect(result.current.session.chatStatus).toBe("idle");
  expect(router.replace).not.toHaveBeenCalled();
});

it("does not override a newer selection when an earlier deletion completes", async () => {
  const waiting = deferred<void>();
  const { result, router } = renderDeletion(() => waiting.promise);
  await act(async () => { await result.current.session.selectCaseChat("a"); });
  await tick();
  let deleted!: Promise<void>;
  act(() => { deleted = result.current.deletion.confirmDelete(); });
  await act(async () => { await result.current.session.selectCaseChat("b"); });
  await tick();
  await act(async () => { waiting.resolve(); await deleted; });
  expect(result.current.session.getActiveCaseChatId()).toBe("b");
  expect(router.replace).not.toHaveBeenCalled();
});
