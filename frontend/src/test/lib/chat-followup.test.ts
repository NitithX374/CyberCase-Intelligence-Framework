import { describe, expect, it } from "vitest";
import type { ChatMessageRead } from "@/lib/api";
import {
  activeCaseChatFollowUp,
  filterSupersededClarificationAnswers,
  followUpGapDetailForMessage,
  latestUserAnswerBetween,
} from "@/lib/chat-followup";

function message(
  ordinal: number,
  role: ChatMessageRead["role"],
  content: string,
  metadata_json: Record<string, unknown> = {},
): ChatMessageRead {
  return {
    id: `message-${ordinal}`,
    case_id: "caseChat-1",
    ordinal,
    role,
    content,
    retrieval_context_id: null,
    message_kind: role === "user" ? "followup_answer" : "conversation",
    analysis_result_id: null,
    metadata_json,
    created_at: `2026-07-31T12:00:${String(ordinal).padStart(2, "0")}Z`,
  };
}

function clarification(
  ordinal: number,
  content: string,
  round: number,
): ChatMessageRead {
  return {
    ...message(ordinal, "assistant", content),
    message_kind: "followup_question",
    metadata_json: {
      action: "follow_up",
      chat_followup: {
        root_ordinal: 1,
        round,
        source_analysis_id: "analysis-1",
        source_revision: 1,
        gap: {
          gap_id: "gap-1",
          gap_key: "affected_host",
          topic: "affected host",
          status: "NOT_PROVIDED",
          description: "The affected host was not provided.",
          affects: "The affected host remains unresolved.",
          reason: "The host is needed to scope the incident.",
          priority: "high",
          askable: true,
          clarification_question: content,
        },
      },
    },
  };
}

describe("chat follow-up projection", () => {
  it("keeps a persisted clarification question in the ordinary transcript", () => {
    const messages = [
      message(1, "user", "Investigate this event."),
      clarification(2, "Which host was affected?", 1),
    ];

    expect(filterSupersededClarificationAnswers(messages).map((item) => item.content)).toEqual(
      ["Investigate this event.", "Which host was affected?"],
    );
  });

  it("returns the exact persisted selected gap detail", () => {
    const selectedGapDetail = {
      gap_id: "gap-authentication",
      gap_key: "authentication_records",
      topic: "authentication records",
      status: "NOT_PROVIDED",
      description: "Authentication records were not provided.",
      affects: "The account used for VM access remains unresolved.",
      reason: "The reported access cannot be linked to a specific credential.",
      priority: "high",
      askable: true,
      clarification_question: "Do you have authentication logs?",
    };
    const question = clarification(2, "Do you have authentication logs?", 1);
    question.metadata_json = {
      action: "follow_up",
      chat_followup: {
        root_ordinal: 1,
        round: 1,
        source_analysis_id: "analysis-1",
        source_revision: 1,
        gap: selectedGapDetail,
      },
    };

    expect(followUpGapDetailForMessage(question)).toEqual({
      gapId: "gap-authentication",
      gapKey: "authentication_records",
      topic: selectedGapDetail.topic,
      status: selectedGapDetail.status,
      description: selectedGapDetail.description,
      affects: selectedGapDetail.affects,
      reason: selectedGapDetail.reason,
      priority: selectedGapDetail.priority,
      askable: selectedGapDetail.askable,
      question: selectedGapDetail.clarification_question,
    });
  });

  it("rejects malformed gap metadata without hiding the message", () => {
    const question = clarification(2, "Do you have authentication logs?", 1);
    question.metadata_json = {
      action: "follow_up",
      chat_followup: {
        root_ordinal: 1,
        round: 1,
        source_analysis_id: "analysis-1",
        source_revision: 1,
        gap: { topic: "authentication records" },
      },
    };

    expect(followUpGapDetailForMessage(question)).toBeNull();
    expect(filterSupersededClarificationAnswers([question])).toEqual([question]);
  });

  it("restores a gap without claim links using its reason as the display detail", () => {
    const question = clarification(2, "Do you have authentication logs?", 1);
    question.metadata_json = {
      action: "follow_up",
      chat_followup: {
        root_ordinal: 1,
        round: 1,
        source_analysis_id: "analysis-1",
        source_revision: 1,
        gap: {
          gap_id: "gap-authentication",
          gap_key: "authentication_records",
          topic: "authentication records",
          status: "NOT_PROVIDED",
          description: "Authentication records were not provided.",
          reason: "The reported access cannot be linked to a specific credential.",
          priority: "high",
          askable: true,
          clarification_question: "Do you have authentication logs?",
          affected_claim_ids: [],
        },
      },
    };

    expect(followUpGapDetailForMessage(question)?.affects).toBe(
      "The reported access cannot be linked to a specific credential.",
    );
  });

  it("selects the latest user answer before the next assistant message", () => {
    const question = clarification(2, "Which host was affected?", 1);
    const firstAnswer = message(3, "user", "old-host");
    const editedAnswer = message(4, "user", "edited-host");
    const nextQuestion = clarification(5, "When was it observed?", 2);

    expect(
      latestUserAnswerBetween(
        [nextQuestion, editedAnswer, question, firstAnswer],
        question.ordinal,
        nextQuestion.ordinal,
      ),
    ).toEqual(editedAnswer);

    expect(
      activeCaseChatFollowUp(
        [nextQuestion, editedAnswer, question, firstAnswer],
        "awaiting_followup",
      ),
    ).toMatchObject({
      question: nextQuestion.content,
      gap: { gapId: "gap-1" },
      entries: [{ question: question.content, answer: editedAnswer.content }],
    });
  });

  it("omits superseded retry answers from a terminal metadata-backed transcript", () => {
    const messages = [
      message(1, "user", "Investigate this event."),
      clarification(2, "Which host was affected?", 1),
      message(3, "user", "old-host"),
      message(4, "user", "edited-host"),
      clarification(5, "When was it observed?", 2),
      message(6, "user", "old-time"),
      message(7, "user", "edited-time"),
      message(8, "assistant", "The terminal analysis is complete."),
    ];

    expect(
      filterSupersededClarificationAnswers(messages).map(
        (persistedMessage) => persistedMessage.content,
      ),
    ).toEqual([
      "Investigate this event.",
      "Which host was affected?",
      "edited-host",
      "When was it observed?",
      "edited-time",
      "The terminal analysis is complete.",
    ]);
  });

  it("does not invent a follow-up from metadata-free messages", () => {
    const messages = [
      message(1, "user", "Investigate this event."),
      message(2, "assistant", "The first clarification question."),
      message(3, "assistant", "The latest clarification question."),
    ];

    expect(activeCaseChatFollowUp(messages, "awaiting_followup")).toBeNull();
  });
});
