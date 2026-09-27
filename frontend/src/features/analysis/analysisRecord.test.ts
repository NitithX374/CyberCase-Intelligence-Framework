import { describe, expect, it } from "vitest";
import { analysisResult, followupHistory, sourceId, sourcesRead } from "@/test/fixtures";
import { analysisFollowups, analysisSourceIds } from "./analysisRecord";

describe("what an analysis recorded", () => {
  it("reads the follow-up exchanges it was given", () => {
    const result = analysisResult({
      external_context_json: {
        followup_history: followupHistory("When did it happen?", "At 02:00.", "QA-03"),
      },
    });

    expect(analysisFollowups(result)).toEqual([
      { qaId: "QA-03", question: "When did it happen?", answer: "At 02:00." },
    ]);
  });

  it("reads the case sources it read", () => {
    const result = analysisResult({
      external_context_json: { sources_read: sourcesRead(sourceId) },
    });

    expect(analysisSourceIds(result)).toEqual([sourceId]);
  });

  it("reads nothing from an analysis that recorded nothing", () => {
    const result = analysisResult();

    expect(analysisFollowups(result)).toEqual([]);
    expect(analysisSourceIds(result)).toEqual([]);
  });
});
