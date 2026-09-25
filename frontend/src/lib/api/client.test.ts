import { afterEach, describe, expect, it, vi } from "vitest";
import { createCaseChatMessage, http, startCaseAnalysis } from "./client";

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
