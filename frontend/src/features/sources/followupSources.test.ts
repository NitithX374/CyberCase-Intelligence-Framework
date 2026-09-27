import { describe, expect, it } from "vitest";
import type { ChatMessageRead } from "@/lib/api/types";
import { followupExchange } from "@/test/fixtures";
import { chatFollowups } from "./followupSources";

function conversation(id: string, ordinal: number, role: "user" | "assistant"): ChatMessageRead {
  return {
    id,
    case_id: "case-1",
    ordinal,
    role,
    content: `${role} message`,
    message_kind: "conversation",
    analysis_result_id: null,
    metadata_json: {},
    created_at: "2026-09-10T00:00:00Z",
  };
}

describe("chatFollowups", () => {
  it("names each answered question by the QA id the backend gave it", () => {
    const exchange = followupExchange("Was a warrant issued?", "No.", "arrest_warrant", "QA-04");

    expect(chatFollowups(exchange)).toEqual([
      { qaId: "QA-04", question: "Was a warrant issued?", answer: "No." },
    ]);
  });

  it("leaves out a question nobody has answered yet", () => {
    const [question] = followupExchange("Was a warrant issued?", "No.");

    expect(chatFollowups([question])).toEqual([]);
  });

  it("ignores ordinary conversation, even a reply to a question", () => {
    const user = conversation("m1", 1, "user");
    const reply = { ...conversation("m2", 2, "assistant"), in_reply_to_message_id: "m1" };

    expect(chatFollowups([user, reply])).toEqual([]);
  });
});
