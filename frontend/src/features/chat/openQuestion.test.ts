import { describe, expect, it } from "vitest";

import { openQuestionId } from "./useCaseChat";
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

  it("is not fooled by a question the case moved on from", () => {
    // One case in the database looks exactly like this: a question was asked,
    // an analysis ran before anyone answered it, and that analysis asked a
    // different one. Scanning every message for an unanswered question found
    // the skipped one and never stopped finding it -- so the composer believed
    // the reader was answering a question on every send, for good, and the
    // header said the case was being analysed while it sat idle. The backend
    // reads the latest question only; this has to agree with it.
    const messages = [
      message(1, "assistant", { gap_key: "topic:exfiltrated-data" }),
      message(2, "assistant", { gap_key: "topic:server-count" }),
      message(3, "user", { in_reply_to_message_id: "m2" }),
    ];
    expect(openQuestionId(messages)).toBeNull();
  });

  it("is blind to ordinary conversation", () => {
    const messages = [
      message(1, "user"),
      message(2, "assistant", { in_reply_to_message_id: "m1" }),
    ];
    expect(openQuestionId(messages)).toBeNull();
  });
});
