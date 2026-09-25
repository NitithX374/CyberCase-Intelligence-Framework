import { render } from "@testing-library/react";
import { QueryClient, QueryClientProvider, useMutation } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";
import { useAnalysisRunOutcome } from "./useRunCaseAnalysis";

function Listener() {
  useAnalysisRunOutcome("case-1", {
    onCompleted: vi.fn(),
    onQuestion: vi.fn(),
    onFailed: vi.fn(),
  });
  return null;
}

function LaterMutation() {
  useMutation({ mutationFn: async () => null });
  return null;
}

describe("useAnalysisRunOutcome", () => {
  it("lets another component mount a mutation while it listens", () => {
    const client = new QueryClient();
    const { rerender } = render(
      <QueryClientProvider client={client}>
        <Listener />
      </QueryClientProvider>,
    );

    expect(() =>
      rerender(
        <QueryClientProvider client={client}>
          <Listener />
          <LaterMutation />
        </QueryClientProvider>,
      ),
    ).not.toThrow();
  });
});
