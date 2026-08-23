import { describe, expect, it } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import { buildCaseMaterials } from "@/lib/case-materials";

describe("buildCaseMaterials", () => {
  it("extracts initial case description, clarification response, and additional case info while filtering out asks and assistant messages", () => {
    const messages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "พบการโจมตีผ่านช่องโหว่ IIS Web Server เมื่อวันที่ 10 มีนาคม",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-03-10T08:00:00Z",
      },
      {
        id: "msg-2",
        thread_id: "thread-1",
        ordinal: 2,
        role: "assistant",
        content: "การวิเคราะห์ภาพรวม...",
        retrieval_context_id: "ret-1",
        metadata_json: { analysis_kind: "grounded_main_analysis" },
        created_at: "2026-03-10T08:01:00Z",
      },
      {
        id: "msg-3",
        thread_id: "thread-1",
        ordinal: 3,
        role: "user",
        content: "คนร้ายใช้เทคนิคอะไรในการคงสิทธิ์?",
        retrieval_context_id: null,
        metadata_json: { action: "ask" },
        created_at: "2026-03-10T08:05:00Z",
      },
      {
        id: "msg-4",
        thread_id: "thread-1",
        ordinal: 4,
        role: "assistant",
        content: "คำตอบ...",
        retrieval_context_id: "ret-1",
        metadata_json: {},
        created_at: "2026-03-10T08:06:00Z",
      },
      {
        id: "msg-5",
        thread_id: "thread-1",
        ordinal: 5,
        role: "user",
        content: "เวลาที่เกิดเหตุคาดว่าเป็นช่วง 02:00 น. และพบบัญชี service_admin",
        retrieval_context_id: null,
        metadata_json: {
          action: "answer_followup",
          evidence_kind: "clarification_answer",
        },
        created_at: "2026-03-10T08:10:00Z",
      },
      {
        id: "msg-6",
        thread_id: "thread-1",
        ordinal: 6,
        role: "user",
        content: "ตรวจพบไฟล์ sdbinst.exe เพิ่มเติมในไดเรกทอรี C:\\Windows",
        retrieval_context_id: null,
        metadata_json: {
          action: "add_case_info",
          evidence_kind: "added_case_information",
        },
        created_at: "2026-03-10T08:15:00Z",
      },
    ];

    const result = buildCaseMaterials(messages);
    expect(result.hasMaterials).toBe(true);
    expect(result.totalCount).toBe(3);

    // 1. Initial narrative
    expect(result.items[0].id).toBe("msg-1");
    expect(result.items[0].itemNumber).toBe("01");
    expect(result.items[0].type).toBe("initial_case_description");
    expect(result.items[0].isInitial).toBe(true);
    expect(result.items[0].content).toContain("พบการโจมตีผ่านช่องโหว่ IIS");

    // 2. Clarification response
    expect(result.items[1].id).toBe("msg-5");
    expect(result.items[1].itemNumber).toBe("02");
    expect(result.items[1].type).toBe("clarification_response");
    expect(result.items[1].isInitial).toBe(false);
    expect(result.items[1].content).toContain("เวลาที่เกิดเหตุคาดว่าเป็นช่วง");

    // 3. Additional case information
    expect(result.items[2].id).toBe("msg-6");
    expect(result.items[2].itemNumber).toBe("03");
    expect(result.items[2].type).toBe("additional_case_info");
    expect(result.items[2].content).toContain("sdbinst.exe");
  });

  it("returns empty when no user evidence exists", () => {
    const result = buildCaseMaterials([]);
    expect(result.hasMaterials).toBe(false);
    expect(result.items).toHaveLength(0);
    expect(result.totalCount).toBe(0);
  });
});
