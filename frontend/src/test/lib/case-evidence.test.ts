import { describe, expect, it } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import {
  getCaseEvidenceKind,
  isCaseEvidenceMessage,
  getCaseEvidencePresentation,
} from "@/lib/case-evidence";

function makeUserMessage(
  ordinal: number,
  metadata: Record<string, unknown> = {},
  content = "Test content",
): PersistedChatMessage {
  return {
    id: `msg-${ordinal}`,
    thread_id: "thread-1",
    ordinal,
    role: "user",
    content,
    retrieval_context_id: null,
    metadata_json: metadata,
    created_at: "2026-08-24T06:00:00Z",
  };
}

function makeAssistantMessage(
  ordinal: number,
  metadata: Record<string, unknown> = {},
  content = "Assistant response",
): PersistedChatMessage {
  return {
    id: `msg-${ordinal}`,
    thread_id: "thread-1",
    ordinal,
    role: "assistant",
    content,
    retrieval_context_id: "rc-1",
    metadata_json: metadata,
    created_at: "2026-08-24T06:01:00Z",
  };
}

describe("case-evidence canonical classifier", () => {
  it("classifies initial_case_narrative as case evidence", () => {
    const msg = makeUserMessage(1, { evidence_kind: "initial_case_narrative" });
    expect(getCaseEvidenceKind(msg)).toBe("initial_case_narrative");
    expect(isCaseEvidenceMessage(msg)).toBe(true);

    const presentation = getCaseEvidencePresentation(msg);
    expect(presentation).not.toBeNull();
    expect(presentation?.kind).toBe("initial_case_narrative");
    expect(presentation?.sourceType).toBe("case_description");
    expect(presentation?.materialType).toBe("initial_case_description");
    expect(presentation?.isInitial).toBe(true);
    expect(presentation?.label).toBe("Initial case description");
    expect(presentation?.overviewSourceLabel).toBe("Case description");
    expect(presentation?.sourceTypeLabel).toContain("รายละเอียดคดีเริ่มต้น");
  });

  it("classifies clarification_answer as case evidence", () => {
    const msg = makeUserMessage(3, { evidence_kind: "clarification_answer" });
    expect(getCaseEvidenceKind(msg)).toBe("clarification_answer");
    expect(isCaseEvidenceMessage(msg)).toBe(true);

    const presentation = getCaseEvidencePresentation(msg);
    expect(presentation).not.toBeNull();
    expect(presentation?.kind).toBe("clarification_answer");
    expect(presentation?.sourceType).toBe("clarification_response");
    expect(presentation?.materialType).toBe("clarification_response");
    expect(presentation?.isInitial).toBe(false);
    expect(presentation?.label).toBe("Clarification response");
    expect(presentation?.overviewSourceLabel).toBe("Clarification");
    expect(presentation?.sourceTypeLabel).toContain("คำตอบชี้แจงเพิ่มเติม");
  });

  it("classifies added_case_information as case evidence", () => {
    const msg = makeUserMessage(5, { evidence_kind: "added_case_information" });
    expect(getCaseEvidenceKind(msg)).toBe("added_case_information");
    expect(isCaseEvidenceMessage(msg)).toBe(true);

    const presentation = getCaseEvidencePresentation(msg);
    expect(presentation).not.toBeNull();
    expect(presentation?.kind).toBe("added_case_information");
    expect(presentation?.sourceType).toBe("additional_info");
    expect(presentation?.materialType).toBe("additional_case_info");
    expect(presentation?.isInitial).toBe(false);
    expect(presentation?.label).toBe("Evidence #5");
    expect(presentation?.overviewSourceLabel).toBe("Evidence #5");
    expect(presentation?.sourceTypeLabel).toContain("ข้อมูลคดีเพิ่มเติม");
  });

  it("excludes analyst_question completely from case evidence", () => {
    const msg = makeUserMessage(3, { evidence_kind: "analyst_question" });
    expect(getCaseEvidenceKind(msg)).toBeNull();
    expect(isCaseEvidenceMessage(msg)).toBe(false);
    expect(getCaseEvidencePresentation(msg)).toBeNull();
  });

  it("excludes assistant messages completely from case evidence", () => {
    const msg = makeAssistantMessage(2, {
      evidence_kind: "initial_case_narrative",
      analysis_kind: "grounded_main_analysis",
    });
    expect(getCaseEvidenceKind(msg)).toBeNull();
    expect(isCaseEvidenceMessage(msg)).toBe(false);
    expect(getCaseEvidencePresentation(msg)).toBeNull();
  });

  it("applies narrow legacy-safe rule for ordinal 1 user message without evidence_kind", () => {
    const msg = makeUserMessage(1, {});
    expect(getCaseEvidenceKind(msg)).toBe("initial_case_narrative");
    expect(isCaseEvidenceMessage(msg)).toBe(true);
    expect(getCaseEvidencePresentation(msg)?.sourceType).toBe("case_description");
  });

  it("fails closed on non-ordinal-1 user message with missing or unknown metadata", () => {
    const emptyMetaMsg = makeUserMessage(3, {});
    expect(getCaseEvidenceKind(emptyMetaMsg)).toBeNull();
    expect(isCaseEvidenceMessage(emptyMetaMsg)).toBe(false);
    expect(getCaseEvidencePresentation(emptyMetaMsg)).toBeNull();

    const unknownMetaMsg = makeUserMessage(4, { evidence_kind: "unknown_custom_kind" });
    expect(getCaseEvidenceKind(unknownMetaMsg)).toBeNull();
    expect(isCaseEvidenceMessage(unknownMetaMsg)).toBe(false);
    expect(getCaseEvidencePresentation(unknownMetaMsg)).toBeNull();

    const actionOnlyMsg = makeUserMessage(5, { action: "ask" });
    expect(getCaseEvidenceKind(actionOnlyMsg)).toBeNull();
    expect(isCaseEvidenceMessage(actionOnlyMsg)).toBe(false);
    expect(getCaseEvidencePresentation(actionOnlyMsg)).toBeNull();
  });
});
