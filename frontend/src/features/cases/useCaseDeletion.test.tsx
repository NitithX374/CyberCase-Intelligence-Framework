import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, renderHook } from "@testing-library/react";
import { useState, type ReactNode } from "react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import type { CaseRead } from "@/lib/api";
import { useCaseDeletion } from "./useCaseDeletion";

beforeEach(() => {
  vi.useFakeTimers();
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.restoreAllMocks();
});

function caseRecord(id: string): CaseRead {
  return {
    id,
    title: `Case ${id}`,
    status: "idle",
    source_revision: 1,
    analysis_freshness: "current",
    created_at: "2026-09-05T00:00:00Z",
    updated_at: "2026-09-05T00:00:00Z",
  };
}

function renderDeletion(
  deleteThread: (id: string) => Promise<void>,
  options: { activeCaseId?: string | null; cases?: CaseRead[] } = {},
) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity } },
  });
  const router = { replace: vi.fn() };
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  const hook = renderHook(
    () => {
      const [candidate, setCandidate] = useState<CaseRead | null>(caseRecord("a"));
      const deletion = useCaseDeletion({
        deleteCandidate: candidate,
        setDeleteCandidate: setCandidate,
        deletingCaseId: null,
        activeView: "analysis",
        activeCaseId: options.activeCaseId ?? "a",
        cases: options.cases ?? [caseRecord("a"), caseRecord("b")],
        deleteCase: deleteThread,
        router,
      });
      return { deletion, candidate, setCandidate };
    },
    { wrapper },
  );
  return { ...hook, router };
}

it("routes to the remaining case after deleting the active case", async () => {
  const remove = vi.fn().mockResolvedValue(undefined);
  const { result, router } = renderDeletion(remove);

  await act(async () => {
    await result.current.deletion.confirmDelete();
  });

  expect(remove).toHaveBeenCalledWith("a");
  expect(result.current.candidate).toBeNull();
  expect(router.replace).toHaveBeenCalledWith("/case/b/analysis");
});

it("routes to /case when no remaining cases exist", async () => {
  const remove = vi.fn().mockResolvedValue(undefined);
  const { result, router } = renderDeletion(remove, { cases: [caseRecord("a")] });

  await act(async () => {
    await result.current.deletion.confirmDelete();
  });

  expect(remove).toHaveBeenCalledWith("a");
  expect(result.current.candidate).toBeNull();
  expect(router.replace).toHaveBeenCalledWith("/case");
});

it("does not navigate after a failed deletion", async () => {
  const { result, router } = renderDeletion(vi.fn().mockRejectedValue(new Error("Delete failed")));

  await act(async () => {
    await result.current.deletion.confirmDelete();
  });

  expect(result.current.candidate).toBeNull();
  expect(router.replace).not.toHaveBeenCalled();
});

it("does not navigate if the deleted case was not active", async () => {
  const remove = vi.fn().mockResolvedValue(undefined);
  const { result, router } = renderDeletion(remove, { activeCaseId: "b" });

  await act(async () => {
    await result.current.deletion.confirmDelete();
  });

  expect(remove).toHaveBeenCalledWith("a");
  expect(result.current.candidate).toBeNull();
  expect(router.replace).not.toHaveBeenCalled();
});
