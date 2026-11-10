import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { caseQueryKeys } from "@/lib/queryKeys";
import { AnalysisProgress } from "@/features/analysis/AnalysisProgress";
import type { ReachedStep } from "@/features/analysis/progress";

function renderWith(steps: ReachedStep[] | undefined) {
  const queryClient = new QueryClient();
  if (steps) queryClient.setQueryData(caseQueryKeys.analysisProgress("a"), steps);
  render(
    <QueryClientProvider client={queryClient}>
      <AnalysisProgress caseId="a" />
    </QueryClientProvider>,
  );
}

describe("the progress of a running analysis", () => {
  it("shows nothing before the backend has reported a step", () => {
    renderWith(undefined);

    expect(screen.queryByRole("list", { name: "Analysis progress" })).not.toBeInTheDocument();
  });

  it("lays the steps out in order, marks the one running, and times the ones finished", () => {
    const now = Date.now();
    renderWith([
      { step: "assess", elapsed: 0, reachedAt: now - 30_000 },
      { step: "gate", elapsed: 21, reachedAt: now - 9_000 },
      { step: "retrieve", elapsed: 25, reachedAt: now - 5_000 },
    ]);

    const list = screen.getByRole("list", { name: "Analysis progress" });
    const stages = Array.from(list.children);
    expect(stages.map((stage) => stage.textContent)).toEqual([
      "Check what is missing0:21",
      "Look for technical signs0:04",
      expect.stringMatching(/^Look up ATT&CK and Thai law0:0\d$/),
      "4Read the sources",
      "5Link findings to sources",
      "6At the same timeScreen findings against the sourcesList people, dates and impactsWrite the summary",
    ]);
    expect(stages[2]).toHaveAttribute("aria-current", "step");
    expect(stages[0]).not.toHaveAttribute("aria-current");
    expect(within(stages[5] as HTMLElement).getAllByRole("listitem")).toHaveLength(3);
  });
});
