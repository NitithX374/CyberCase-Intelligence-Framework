import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { describe, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { useCaseRunPolling } from "@/hooks/useCaseRunPolling";
import { caseQueryKeys } from "@/hooks/useCaseQueries";

function createWrapper(queryClient: QueryClient) {
  return function Wrapper({ children }: PropsWithChildren) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe("useCaseRunPolling", () => {
  it("invalidates native clarifications when a Case run settles", async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    vi.spyOn(api, "getCaseRun").mockResolvedValue({
      id: "run-1",
      case_id: "case-1",
      operation: "analysis",
      snapshot_id: "snapshot-1",
      request_message_id: null,
      context_analysis_result_id: null,
      clarification_id: null,
      status: "completed",
      attempt_count: 1,
      error_code: null,
      error_message: null,
      created_at: "2026-09-10T01:00:00Z",
      started_at: "2026-09-10T01:00:01Z",
      finished_at: "2026-09-10T01:00:02Z",
      updated_at: "2026-09-10T01:00:02Z",
    });
    const invalidate = vi.spyOn(queryClient, "invalidateQueries");

    renderHook(
      () => useCaseRunPolling("case-1", "run-1", null),
      { wrapper: createWrapper(queryClient) },
    );

    await waitFor(() => expect(invalidate).toHaveBeenCalled());
    expect(invalidate).toHaveBeenCalledWith({
      queryKey: caseQueryKeys.clarifications("case-1"),
    });
  });
});
