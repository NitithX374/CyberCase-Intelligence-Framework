import { describe, expect, it } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import { buildTechnicalContext } from "@/lib/technical-context";

describe("buildTechnicalContext", () => {
  it("extracts admitted MITRE techniques, tactics, concise plain meaning, case-specific relevance, and sources", () => {
    const messages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "พบการบุกรุกเข้าสู่ IIS Web Server โดยคนร้ายใช้ Application Shimming เพื่อฝังตัว",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-03-10T08:00:00Z",
      },
      {
        id: "msg-2",
        thread_id: "thread-1",
        ordinal: 2,
        role: "assistant",
        content: "ผลการวิเคราะห์...",
        retrieval_context_id: "ret-1",
        metadata_json: {
          analysis_kind: "grounded_main_analysis",
          mitre_table: [
            {
              technique_id: "T1190",
              name: "Exploit Public-Facing Application",
              tactic: "Initial Access",
              description: "Abuse of a public-facing application to gain access.",
              reason: "คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server",
            },
            {
              technique_id: "T1546.011",
              name: "Event Triggered Execution: Application Shimming",
              tactic: "Persistence, Privilege Escalation",
              description: "Adversaries may establish persistence using application shims.",
              reason: "พบพฤติกรรมติดตั้ง Application Shim เพื่อคงสิทธิ์",
            },
          ],
          analysis_trace: {
            version: "analysis_trace_v2",
            claims: [
              {
                claim_id: "c1",
                text: "คนร้ายโจมตีผ่านช่องโหว่ IIS",
                claim_type: "event_progression",
                epistemic_status: "reported",
                source_message_ids: ["msg-1"],
              },
            ],
            mitre_associations: [
              {
                association_id: "assoc-1",
                technique_id: "T1190",
                claim_ids: ["c1"],
                reason: "คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server ที่เปิดสู่สาธารณะ",
                status: "candidate",
                support_role: "external_knowledge",
              },
            ],
          },
        },
        created_at: "2026-03-10T08:01:00Z",
      },
    ];

    const result = buildTechnicalContext(messages);
    expect(result.hasContext).toBe(true);
    expect(result.totalCount).toBe(2);

    // Technique 1: T1190 (linked through claim c1 to msg-1)
    const t1190 = result.techniques.find((t) => t.techniqueId === "T1190")!;
    expect(t1190).toBeDefined();
    expect(t1190.techniqueName).toBe("Exploit Public-Facing Application");
    expect(t1190.tactic).toBe("Initial Access");
    expect(t1190.shortPlainMeaning).toBe("Abuse of a public-facing application to gain access.");
    expect(t1190.whyRelevantHere).toContain("คนร้ายโจมตีผ่านช่องโหว่ IIS Web Server");
    expect(t1190.caseBasisSources).toHaveLength(1);
    expect(t1190.caseBasisSources[0].id).toBe("msg-1");
    expect(t1190.isExternalReference).toBe(true);

    // Technique 2: T1546.011 (no association/claims -> zero caseBasisSources, NO fake fallback)
    const t1546 = result.techniques.find((t) => t.techniqueId === "T1546.011")!;
    expect(t1546).toBeDefined();
    expect(t1546.tactic).toContain("Persistence");
    expect(t1546.caseBasisSources).toHaveLength(0);
  });

  it("proves unlinked MITRE techniques or associations linking to analyst_question get zero caseBasisSources", () => {
    const messages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "Initial incident",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-03-10T08:00:00Z",
      },
      {
        id: "msg-2",
        thread_id: "thread-1",
        ordinal: 2,
        role: "user",
        content: "Did the attacker use discovery techniques?",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "analyst_question" },
        created_at: "2026-03-10T08:05:00Z",
      },
      {
        id: "msg-3",
        thread_id: "thread-1",
        ordinal: 3,
        role: "assistant",
        content: "Analysis...",
        retrieval_context_id: "ret-1",
        metadata_json: {
          analysis_kind: "grounded_main_analysis",
          mitre_table: [
            {
              technique_id: "T1018",
              name: "Remote System Discovery",
              tactic: "Discovery",
              description: "Discovery description",
              reason: "Discovery reason",
            },
          ],
          analysis_trace: {
            version: "analysis_trace_v2",
            claims: [
              {
                claim_id: "c2",
                text: "Discovery query",
                claim_type: "event_progression",
                epistemic_status: "reported",
                source_message_ids: ["msg-2"],
              },
            ],
            mitre_associations: [
              {
                association_id: "assoc-2",
                technique_id: "T1018",
                claim_ids: ["c2"],
                reason: "Discovery note",
                status: "candidate",
                support_role: "external_knowledge",
              },
            ],
          },
        },
        created_at: "2026-03-10T08:10:00Z",
      },
    ];

    const result = buildTechnicalContext(messages);
    expect(result.techniques[0].techniqueId).toBe("T1018");
    // Since msg-2 is an analyst_question, it must NOT be included as a source
    expect(result.techniques[0].caseBasisSources).toHaveLength(0);
  });

  it("returns conservative fallback when reason contains generic filler", () => {
    const messages: PersistedChatMessage[] = [
      {
        id: "msg-1",
        thread_id: "thread-1",
        ordinal: 1,
        role: "user",
        content: "พบพฤติกรรม...",
        retrieval_context_id: null,
        metadata_json: { evidence_kind: "initial_case_narrative" },
        created_at: "2026-03-10T08:00:00Z",
      },
      {
        id: "msg-2",
        thread_id: "thread-1",
        ordinal: 2,
        role: "assistant",
        content: "ผล...",
        retrieval_context_id: "ret-1",
        metadata_json: {
          analysis_kind: "grounded_main_analysis",
          mitre_table: [
            {
              technique_id: "T1018",
              name: "Remote System Discovery",
              tactic: "Discovery",
              description: "Adversaries may attempt to get a listing of other systems.",
              reason: "เทคนิคนี้ถูกนำมาใช้เป็นกรอบอ้างอิงเชิงวิเคราะห์เพื่ออธิบายพฤติกรรมการโจมตีที่สอดคล้องกับข้อมูลในสำนวนคดี",
            },
          ],
        },
        created_at: "2026-03-10T08:01:00Z",
      },
    ];

    const result = buildTechnicalContext(messages);
    expect(result.techniques[0].whyRelevantHere).toBe("พบพฤติกรรมในข้อมูลคดีที่สอดคล้องกับเทคนิคนี้");
  });

  it("returns empty when no analysis message exists", () => {
    const result = buildTechnicalContext([]);
    expect(result.hasContext).toBe(false);
    expect(result.techniques).toHaveLength(0);
    expect(result.totalCount).toBe(0);
  });
});
