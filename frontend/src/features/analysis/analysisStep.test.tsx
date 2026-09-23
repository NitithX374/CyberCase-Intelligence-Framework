/**
 * An analysis that paused to ask something is not a finished analysis.
 *
 * The mutation used to write whatever the POST returned straight into the
 * analysis cache, on the reasoning that the analysis was over by the time it
 * resolved. It is not over any more: a step can come back holding a question
 * and no result, and writing that envelope into the cache renders the overview
 * as "Analysis unavailable" over a case that is merely mid-clarification.
 */

import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { act } from "react";
import type { ReactNode } from "react";
import { beforeEach, expect, it, vi } from "vitest";
import { caseQueryKeys } from "@/lib/queryKeys";
import { useStartCaseAnalysis } from "@/features/analysis/queries";
import type { AnalysisStepRead, CaseAnalysisResultRead } from "@/lib/api";

const startCaseAnalysis = vi.fn();

vi.mock("@/lib/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/api")>()),
  startCaseAnalysis: (...args: unknown[]) => startCaseAnalysis(...args),
}));

const RESULT = {
  id: "r1",
  case_id: "a",
  source_revision: 1,
  schema_version: "case_analysis_trace_v1",
  status: "validated",
  answer: "Files were encrypted.",
  summary: "Files were encrypted.",
  trace_json: null,
  retrieval_context_id: null,
  pipeline_config: {},
  external_context_json: {},
  created_at: new Date().toISOString(),
  freshness: "current",
} as CaseAnalysisResultRead;

const PAUSED: AnalysisStepRead = {
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

const FINISHED: AnalysisStepRead = {
  status: "completed",
  round: 2,
  max_rounds: 3,
  stop_reason: "gaps_exhausted",
  result: RESULT,
};

function render() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: Infinity }, mutations: { retry: false } },
  });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  return { ...renderHook(() => useStartCaseAnalysis("a"), { wrapper }), queryClient };
}

beforeEach(() => {
  vi.clearAllMocks();
});

it("leaves the analysis cache alone while the case is still being clarified", async () => {
  startCaseAnalysis.mockResolvedValue(PAUSED);
  const { result, queryClient } = render();

  await act(async () => {
    await result.current.mutateAsync({ response_language: "english" });
  });

  expect(queryClient.getQueryData(caseQueryKeys.analysis("a"))).toBeUndefined();
});

it("returns the question so the caller can open the chat instead of navigating", async () => {
  startCaseAnalysis.mockResolvedValue(PAUSED);
  const { result } = render();

  const step = await act(async () => result.current.mutateAsync({ response_language: "english" }));

  expect(step.status).toBe("need_followup");
  expect(step.question?.question).toBe("When did the incident happen?");
  expect(step.round).toBe(1);
});

it("caches the result once the clarification has terminated", async () => {
  startCaseAnalysis.mockResolvedValue(FINISHED);
  const { result, queryClient } = render();

  await act(async () => {
    await result.current.mutateAsync({ response_language: "english" });
  });

  await waitFor(() =>
    expect(queryClient.getQueryData(caseQueryKeys.analysis("a"))).toEqual(RESULT),
  );
});
