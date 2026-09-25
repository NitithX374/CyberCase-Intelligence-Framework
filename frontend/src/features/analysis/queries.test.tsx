import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { act, type ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { AnalysisStepRead } from "@/lib/api";
import { caseQueryKeys } from "@/lib/queryKeys";
import { analysisResult } from "@/test/fixtures";
import { deferred } from "@/features/chat/chatTestSupport";
import { useIsCaseAnalysisRunning, useStartCaseAnalysis } from "./queries";

const startCaseAnalysis = vi.fn();

vi.mock("@/lib/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/api")>()),
  startCaseAnalysis: (...args: unknown[]) => startCaseAnalysis(...args),
}));

const PAUSED: AnalysisStepRead = { status: "need_followup" };

const RESULT = analysisResult({ id: "r1", case_id: "a" });

const FINISHED: AnalysisStepRead = { status: "completed", result: RESULT };

function setup() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  return { queryClient, wrapper };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("starting an analysis", () => {
  it("leaves the analysis cache alone while the case is still being clarified", async () => {
    startCaseAnalysis.mockResolvedValue(PAUSED);
    const { queryClient, wrapper } = setup();
    const { result } = renderHook(() => useStartCaseAnalysis("a"), { wrapper });

    await act(async () => {
      await result.current.mutateAsync();
    });

    expect(queryClient.getQueryData(caseQueryKeys.analysis("a"))).toBeUndefined();
  });

  it("caches the result once the clarification has terminated", async () => {
    startCaseAnalysis.mockResolvedValue(FINISHED);
    const { queryClient, wrapper } = setup();
    const { result } = renderHook(() => useStartCaseAnalysis("a"), { wrapper });

    await act(async () => {
      await result.current.mutateAsync();
    });

    await waitFor(() =>
      expect(queryClient.getQueryData(caseQueryKeys.analysis("a"))).toEqual(RESULT),
    );
  });

  it("sends no language, because the backend decides it from the sources", async () => {
    startCaseAnalysis.mockResolvedValue(FINISHED);
    const { wrapper } = setup();
    const { result } = renderHook(() => useStartCaseAnalysis("a"), { wrapper });

    await act(async () => {
      await result.current.mutateAsync();
    });

    expect(startCaseAnalysis).toHaveBeenCalledWith("a");
  });
});

describe("whether an analysis is running", () => {
  it("still reports the run after the component that started it is gone", async () => {
    const call = deferred<AnalysisStepRead>();
    startCaseAnalysis.mockReturnValue(call.promise);
    const { wrapper } = setup();

    const starter = renderHook(() => useStartCaseAnalysis("a"), { wrapper });
    const watcher = renderHook(() => useIsCaseAnalysisRunning("a"), { wrapper });

    expect(watcher.result.current).toBe(false);
    act(() => {
      starter.result.current.mutate();
    });
    await waitFor(() => expect(watcher.result.current).toBe(true));

    starter.unmount();

    const remounted = renderHook(() => useIsCaseAnalysisRunning("a"), { wrapper });
    expect(remounted.result.current).toBe(true);

    const freshObserver = renderHook(() => useStartCaseAnalysis("a"), { wrapper });
    expect(freshObserver.result.current.isPending).toBe(false);

    await act(async () => {
      call.resolve(PAUSED);
    });
    await waitFor(() => expect(remounted.result.current).toBe(false));
  });

  it("answers per case, so one case running does not disable another", async () => {
    const call = deferred<AnalysisStepRead>();
    startCaseAnalysis.mockReturnValue(call.promise);
    const { wrapper } = setup();

    const starter = renderHook(() => useStartCaseAnalysis("a"), { wrapper });
    const running = renderHook(() => useIsCaseAnalysisRunning("a"), { wrapper });
    const other = renderHook(() => useIsCaseAnalysisRunning("b"), { wrapper });

    act(() => {
      starter.result.current.mutate();
    });
    await waitFor(() => expect(running.result.current).toBe(true));
    expect(other.result.current).toBe(false);

    await act(async () => {
      call.resolve(PAUSED);
    });
  });

  it("reports nothing running when there is no case", () => {
    const { wrapper } = setup();
    const { result } = renderHook(() => useIsCaseAnalysisRunning(null), { wrapper });
    expect(result.current).toBe(false);
  });
});
