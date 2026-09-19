import { describe, expect, it } from "vitest";

import { openQuestionId } from "@/hooks/useCaseChat";
import type { ChatMessageRead } from "@/lib/api";

function message(
  ordinal: number,
  role: "user" | "assistant",
  overrides: Partial<ChatMessageRead> = {},
): ChatMessageRead {
  return {
    id: `m${ordinal}`,
    case_id: "case-1",
    ordinal,
    role,
    content: role === "user" ? "An answer." : "A message.",
    message_kind: "conversation",
    analysis_result_id: null,
    in_reply_to_message_id: null,
    metadata_json: {},
    retrieval_context_id: null,
    created_at: "2026-09-19T00:00:00Z",
    ...overrides,
  };
}

describe("openQuestionId", () => {
  it("finds the question the analysis is waiting on", () => {
    const messages = [message(1, "assistant", { gap_key: "topic:incident-time" })];
    expect(openQuestionId(messages)).toBe("m1");
  });

  it("ignores a question that has already been answered", () => {
    const messages = [
      message(1, "assistant", { gap_key: "topic:incident-time" }),
      message(2, "user", { in_reply_to_message_id: "m1" }),
    ];
    expect(openQuestionId(messages)).toBeNull();
  });

  it("moves to the next question of the round", () => {
    const messages = [
      message(1, "assistant", { gap_key: "topic:incident-time" }),
      message(2, "user", { in_reply_to_message_id: "m1" }),
      message(3, "assistant", { gap_key: "topic:account" }),
    ];
    expect(openQuestionId(messages)).toBe("m3");
  });

  it("is blind to ordinary conversation", () => {
    const messages = [
      message(1, "user"),
      message(2, "assistant", { in_reply_to_message_id: "m1" }),
    ];
    expect(openQuestionId(messages)).toBeNull();
  });
});
