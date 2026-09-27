import { afterEach, describe, expect, it, vi } from "vitest";
import { startCaseAnalysis } from "@/features/analysis/api";
import { createCaseChatMessage } from "@/features/chat/api";
import { uploadCaseDocument } from "@/features/sources/api";
import { http } from "./http";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("the requests that start work on a case", () => {
  it("sends a chat message without a language, whatever it is written in", async () => {
    const post = vi.spyOn(http, "post").mockResolvedValue({ data: { messages: [] } });

    await createCaseChatMessage("case-1", "02:00", "key-1");

    expect(post).toHaveBeenCalledWith(
      "/cases/case-1/chat/messages",
      { content: "02:00", client_request_id: "key-1" },
      expect.anything(),
    );
  });

  it("starts an analysis without a language, because the backend decides it", async () => {
    const post = vi.spyOn(http, "post").mockResolvedValue({ data: { status: "need_followup" } });

    await startCaseAnalysis("case-1");

    expect(post).toHaveBeenCalledWith("/cases/case-1/analysis", {}, expect.anything());
  });
});

describe("how long the browser waits for work the backend is still doing", () => {
  const modelStages = 3;
  const modelStageAttempts = 2;
  const modelStageTimeoutMs = 120_000;
  const technicalContextTimeoutMs = 300_000;
  const analysisWorstCaseMs =
    modelStages * modelStageAttempts * modelStageTimeoutMs + technicalContextTimeoutMs;
  const uploadWorstCaseMs = Math.ceil(50 / 4) * 60_000;

  function timeoutOf(post: ReturnType<typeof vi.spyOn>): number {
    const [, , config] = post.mock.calls[0] as [string, unknown, { timeout?: number }];
    return config.timeout ?? 0;
  }

  it("waits for an analysis longer than every stage of it can take", async () => {
    const post = vi.spyOn(http, "post").mockResolvedValue({ data: { status: "need_followup" } });

    await startCaseAnalysis("case-1");

    expect(timeoutOf(post)).toBeGreaterThan(analysisWorstCaseMs);
  });

  it("waits for an answer that closes a round as long as for the analysis it runs", async () => {
    const post = vi.spyOn(http, "post").mockResolvedValue({ data: { messages: [] } });

    await createCaseChatMessage("case-1", "02:00", "key-1");

    expect(timeoutOf(post)).toBeGreaterThan(analysisWorstCaseMs);
  });

  it("waits for an upload longer than reading the longest scan it accepts", async () => {
    const post = vi.spyOn(http, "post").mockResolvedValue({ data: {} });

    await uploadCaseDocument("case-1", new File(["%PDF"], "scan.pdf"));

    expect(timeoutOf(post)).toBeGreaterThan(uploadWorstCaseMs);
  });
});
