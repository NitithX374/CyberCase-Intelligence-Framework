/**
 * A running analysis belongs to the case, not to the page that started it.
 *
 * The header read `useStartCaseAnalysis(...).isPending`, which is one
 * component's view of the run. Open another case and come back and that
 * observer is a new one: the analysis was still running on the server, and the
 * header offered to start it again. The mutation itself outlives the component
 * in the mutation cache, so the question "is this case being analysed" is
 * answered from the cache, keyed by case.
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { act } from "react";
import type { ReactNode } from "react";
import { beforeEach, expect, it, vi } from "vitest";
import { useIsCaseAnalysisRunning, useStartCaseAnalysis } from "@/hooks/useCaseQueries";
import type { AnalysisStepRead } from "@/lib/api";

const startCaseAnalysis = vi.fn();

vi.mock("@/lib/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/api")>()),
  startCaseAnalysis: (...args: unknown[]) => startCaseAnalysis(...args),
}));

const FINISHED: AnalysisStepRead = {
  status: "need_followup",
  round: 1,
  max_rounds: 3,
  question: {
    message_id: "m1",
    gap_id: "G-01",
    gap_key: "topic:incident-time",
    question: "When did the incident happen?",
  },
};

function client() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
}

function wrapperFor(queryClient: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

/** A request the test finishes by hand, so the run can be observed mid-flight. */
function pendingCall() {
  let finish: (step: AnalysisStepRead) => void = () => {};
  startCaseAnalysis.mockImplementation(
    () =>
      new Promise<AnalysisStepRead>((resolve) => {
        finish = resolve;
      }),
  );
  return { finish: (step: AnalysisStepRead) => finish(step) };
}

beforeEach(() => {
  vi.clearAllMocks();
});

it("still reports the run after the component that started it is gone", async () => {
  const queryClient = client();
  const wrapper = wrapperFor(queryClient);
  const call = pendingCall();

  const starter = renderHook(() => useStartCaseAnalysis("a"), { wrapper });
  const watcher = renderHook(() => useIsCaseAnalysisRunning("a"), { wrapper });

  expect(watcher.result.current).toBe(false);
  act(() => {
    starter.result.current.mutate({ response_language: "english" });
  });
  await waitFor(() => expect(watcher.result.current).toBe(true));

  // The reader opens another case. The page holding the mutation goes away.
  starter.unmount();

  const remounted = renderHook(() => useIsCaseAnalysisRunning("a"), { wrapper });
  expect(remounted.result.current).toBe(true);

  // And the reason the hook exists: a fresh observer of the same mutation
  // reports nothing pending, which is what the header used to believe.
  const freshObserver = renderHook(() => useStartCaseAnalysis("a"), { wrapper });
  expect(freshObserver.result.current.isPending).toBe(false);

  await act(async () => {
    call.finish(FINISHED);
  });
  await waitFor(() => expect(remounted.result.current).toBe(false));
});

it("answers per case, so one case running does not disable another", async () => {
  const queryClient = client();
  const wrapper = wrapperFor(queryClient);
  const call = pendingCall();

  const starter = renderHook(() => useStartCaseAnalysis("a"), { wrapper });
  const other = renderHook(() => useIsCaseAnalysisRunning("b"), { wrapper });

  act(() => {
    starter.result.current.mutate({ response_language: "english" });
  });
  await waitFor(() =>
    expect(renderHook(() => useIsCaseAnalysisRunning("a"), { wrapper }).result.current).toBe(true),
  );
  expect(other.result.current).toBe(false);

  await act(async () => {
    call.finish(FINISHED);
  });
});

it("reports nothing running when there is no case", () => {
  const wrapper = wrapperFor(client());
  const { result } = renderHook(() => useIsCaseAnalysisRunning(null), { wrapper });
  expect(result.current).toBe(false);
});
