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

  it("names each step, marks the one running, and times the ones finished", () => {
    const now = Date.now();
    renderWith([
      { step: "assess", elapsed: 0, reachedAt: now - 30_000 },
      { step: "gate", elapsed: 21, reachedAt: now - 9_000 },
      { step: "retrieve", elapsed: 25, reachedAt: now - 5_000 },
    ]);

    const items = within(screen.getByRole("list", { name: "Analysis progress" })).getAllByRole(
      "listitem",
    );
    expect(items.map((item) => item.textContent)).toEqual([
      "Checking what the case is missing0:21",
      "Checking whether ATT&CK applies0:04",
      "Retrieving ATT&CK context0:00",
      "Reading sources: claims and source unit IDs",
      "Binding claims to original source text",
      "Organizing claim information for Details",
      "Judging: summary, open questions, ATT&CK",
    ]);
    expect(items[2]).toHaveAttribute("aria-current", "step");
    expect(items[0]).not.toHaveAttribute("aria-current");
  });
});
