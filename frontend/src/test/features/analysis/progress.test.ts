import { QueryClient } from "@tanstack/react-query";
import { describe, expect, it } from "vitest";
import { caseQueryKeys } from "@/lib/queryKeys";
import {
  clearProgress,
  formatElapsed,
  progressRows,
  recordStep,
  type ReachedStep,
} from "@/features/analysis/progress";

describe("the steps an analysis has reached", () => {
  it("lists every planned step, with retrieval only when the RAG service was asked", () => {
    const reached: ReachedStep[] = [
      { step: "assess", elapsed: 0, reachedAt: 1_000 },
      { step: "gate", elapsed: 20, reachedAt: 21_000 },
    ];

    expect(progressRows(reached, 25_000).map((row) => row.step)).toEqual([
      "assess",
      "gate",
      "read",
      "bind",
      "judge",
    ]);
    expect(
      progressRows([...reached, { step: "retrieve", elapsed: 29, reachedAt: 30_000 }], 31_000).map(
        (row) => row.step,
      ),
    ).toEqual(["assess", "gate", "retrieve", "read", "bind", "judge"]);
  });

  it("leaves out the first step when the analysis went on without it", () => {
    const rows = progressRows(
      [
        { step: "gate", elapsed: 0, reachedAt: 1_000 },
        { step: "read", elapsed: 4, reachedAt: 5_000 },
      ],
      8_000,
    );

    expect(rows.map((row) => row.step)).toEqual(["gate", "read", "bind", "judge"]);
    expect(rows.map((row) => row.state)).toEqual(["done", "current", "waiting", "waiting"]);
  });

  it("still shows the first step while nothing has been reached", () => {
    expect(progressRows([], 0).map((row) => row.step)).toEqual([
      "assess",
      "gate",
      "read",
      "bind",
      "judge",
    ]);
  });

  it("times a finished step by the server and the current one from when it arrived", () => {
    const rows = progressRows(
      [
        { step: "assess", elapsed: 0.5, reachedAt: 1_000 },
        { step: "gate", elapsed: 21.5, reachedAt: 22_000 },
        { step: "read", elapsed: 30, reachedAt: 31_000 },
      ],
      103_000,
    );

    expect(rows.map(({ step, state, seconds }) => ({ step, state, seconds }))).toEqual([
      { step: "assess", state: "done", seconds: 21 },
      { step: "gate", state: "done", seconds: 8.5 },
      { step: "read", state: "current", seconds: 72 },
      { step: "bind", state: "waiting", seconds: null },
      { step: "judge", state: "waiting", seconds: null },
    ]);
  });

  it("writes minutes and seconds", () => {
    expect([0, 9.9, 72.4, 725].map(formatElapsed)).toEqual(["0:00", "0:09", "1:12", "12:05"]);
  });

  it("keeps only the steps it knows, and forgets them all when told", () => {
    const queryClient = new QueryClient();
    recordStep(queryClient, "a", { step: "assess", elapsed: 0 });
    recordStep(queryClient, "a", { step: "something_new", elapsed: 1 });

    expect(
      queryClient
        .getQueryData<ReachedStep[]>(caseQueryKeys.analysisProgress("a"))
        ?.map((reached) => reached.step),
    ).toEqual(["assess"]);

    clearProgress(queryClient, "a");
    expect(queryClient.getQueryData(caseQueryKeys.analysisProgress("a"))).toEqual([]);
  });
});
