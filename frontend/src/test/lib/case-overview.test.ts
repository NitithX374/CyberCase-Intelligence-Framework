import { describe, expect, it } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import { buildCaseOverview } from "@/lib/case-overview";

describe("case-overview view model builder", () => {
  it("returns empty overview data when no messages exist", () => {
    const overview = buildCaseOverview([], "idle");
    expect(overview.hasAnalysis).toBe(false);
    expect(overview.isProcessing).toBe(false);
    expect(overview.incidentSummary).toBe("");
    expect(overview.attackStory).toEqual([]);
    expect(overview.establishedFacts).toEqual([]);
    expect(overview.unclearItems).toEqual([]);
    expect(overview.investigationPoints).toEqual([]);
    expect(overview.mitreContext).toEqual([]);
  });

  it("handles processing state when analysis is running", () => {
    const userMsg: PersistedChatMessage = {
      id: "msg-user-1",
      thread_id: "thread-1",
      ordinal: 1,
      role: "user",
      content: "Attacker compromised public web server.",
      retrieval_context_id: null,
      metadata_json: { evidence_kind: "initial_case_narrative" },
      created_at: "2026-08-23T10:00:00Z",
    };
    const overview = buildCaseOverview([userMsg], "processing");
    expect(overview.hasAnalysis).toBe(false);
    expect(overview.isProcessing).toBe(true);
  });

  it("extracts complete prosecutor case overview from validated analysis message", () => {
    const userMsg1: PersistedChatMessage = {
      id: "msg-user-1",
      thread_id: "thread-1",
      ordinal: 1,
      role: "user",
      content: "Unauthorized activity detected on public-facing IIS server. Application shimming was observed on host WEB-01.",
      retrieval_context_id: null,
      metadata_json: { evidence_kind: "initial_case_narrative" },
      created_at: "2026-08-23T10:00:00Z",
    };

    const assistantAnalysisMsg: PersistedChatMessage = {
      id: "msg-asst-2",
      thread_id: "thread-1",
      ordinal: 2,
      role: "assistant",
      content: `### 1. Overall Case Picture (ภาพรวมคดี)
The attacker reportedly accessed the target IIS web server and deployed persistence mechanisms using Application Shimming.

### 2. Key Sequence and Relationships (ลำดับเหตุการณ์และความสัมพันธ์สำคัญ)
- Initial unauthorized execution occurred on WEB-01.
- Application Shimming was established to retain access across reboots.

### 3. Relevant MITRE ATT&CK Context
Technique T1546.011 was correlated with the shimming activity.

### 4. Unresolved or Conflicting Information
Whether exfiltration occurred to external IPs remains unconfirmed.

### 5. Analytical Boundary
Direct case facts are derived strictly from case report #1.`,
      retrieval_context_id: "rc-1",
      metadata_json: {
        analysis_kind: "grounded_main_analysis",
        analysis_trace: {
          version: "analysis_trace_v2",
          validation_status: "validated",
          analysis_mode: "case_overview",
          retrieval_context_id: "rc-1",
          evidence_sha256: "a".repeat(64),
          claims: [
            {
              claim_id: "A-01",
              claim_type: "reported",
              text: "Unauthorized activity was detected on public IIS server WEB-01.",
              epistemic_status: "reported",
              source_message_ids: ["msg-user-1"],
            },
            {
              claim_id: "A-02",
              claim_type: "reported",
              text: "Application Shimming was configured on WEB-01.",
              epistemic_status: "reported",
              source_message_ids: ["msg-user-1"],
            },
            {
              claim_id: "A-03",
              claim_type: "analytical_inference",
              text: "Data exfiltration destination remains unconfirmed.",
              epistemic_status: "suspected",
              source_message_ids: [],
            },
          ],
          mitre_associations: [
            {
              association_id: "MA-01",
              technique_id: "T1546.011",
              claim_ids: ["A-02"],
              reason: "Application shimming modifies Windows compatibility database to execute malicious code on startup.",
              status: "candidate_only",
              support_role: "external_technical_context",
            },
          ],
        },
        mitre_table: [
          {
            technique_id: "T1546.011",
            name: "Application Shimming",
            description: "Adversaries may establish persistence or escalate privileges by abusing Microsoft Application Compatibility shims.",
            tactic: "Persistence",
          },
        ],
        chat_followup: {
          gap_analysis: {
            gaps: [
              {
                topic: "Exfiltration Destination",
                status: "NOT_PROVIDED",
                description: "Outbound network destinations and data volumes were not provided.",
                affects: "Assessing data breach scope",
                reason: "Firewall egress logs are missing.",
                priority: "high",
                askable: true,
              },
            ],
          },
        },
      },
      created_at: "2026-08-23T10:01:00Z",
    };

    const overview = buildCaseOverview([userMsg1, assistantAnalysisMsg], "answered");

    expect(overview.hasAnalysis).toBe(true);
    expect(overview.analysisMessageId).toBe("msg-asst-2");

    // 1. What Happened
    expect(overview.incidentSummary).toContain("The attacker reportedly accessed the target IIS web server");

    // 2. Attack Story
    expect(overview.attackStory).toHaveLength(3);
    expect(overview.attackStory[0].stepNumber).toBe(1);
    expect(overview.attackStory[0].text).toBe("Unauthorized activity was detected on public IIS server WEB-01.");
    expect(overview.attackStory[0].claimType).toBe("reported");
    expect(overview.attackStory[0].sourceMessages).toHaveLength(1);
    expect(overview.attackStory[0].sourceMessages[0].label).toBe("Case description");
    expect(overview.attackStory[0].sourceMessages[0].sourceType).toBe("case_description");
    expect(overview.attackStory[0].sourceMessages[0].fullContent).toContain("Unauthorized activity detected on public-facing IIS server");

    expect(overview.attackStory[1].stepNumber).toBe(2);
    expect(overview.attackStory[1].mitreTechniques).toHaveLength(1);
    expect(overview.attackStory[1].mitreTechniques[0].techniqueId).toBe("T1546.011");
    expect(overview.attackStory[1].mitreTechniques[0].techniqueName).toBe("Application Shimming");

    // 3. Established Facts
    expect(overview.establishedFacts).toHaveLength(2);
    expect(overview.establishedFacts[0].text).toContain("Unauthorized activity was detected");
    expect(overview.establishedFacts[1].text).toContain("Application Shimming");

    // 4. Unclear Items
    expect(overview.unclearItems.length).toBeGreaterThanOrEqual(1);
    expect(overview.unclearItems.some((u) => u.description.includes("Outbound network destinations"))).toBe(true);

    // 5. Points for Further Investigation
    expect(overview.investigationPoints.length).toBeGreaterThanOrEqual(1);
    expect(overview.investigationPoints[0].priority).toBe("high");
    expect(overview.investigationPoints[0].rationale).toContain("Assessing data breach scope");

    // 6. MITRE Explained Simply
    expect(overview.mitreContext).toHaveLength(1);
    expect(overview.mitreContext[0].techniqueId).toBe("T1546.011");
    expect(overview.mitreContext[0].isExternalContext).toBe(true);
    expect(overview.mitreContext[0].caseAssociationReason).toContain("Application shimming modifies Windows");
  });

  it("fails closed: does not classify analyst_question or missing messages as evidence sources in overview", () => {
    const userMsg1: PersistedChatMessage = {
      id: "msg-user-1",
      thread_id: "thread-1",
      ordinal: 1,
      role: "user",
      content: "Initial incident narrative",
      retrieval_context_id: null,
      metadata_json: { evidence_kind: "initial_case_narrative" },
      created_at: "2026-08-23T10:00:00Z",
    };

    const analystQuestionMsg: PersistedChatMessage = {
      id: "msg-user-2",
      thread_id: "thread-1",
      ordinal: 2,
      role: "user",
      content: "What is the IOC for this?",
      retrieval_context_id: null,
      metadata_json: { evidence_kind: "analyst_question" },
      created_at: "2026-08-23T10:05:00Z",
    };

    const clarificationAnswerMsg: PersistedChatMessage = {
      id: "msg-user-3",
      thread_id: "thread-1",
      ordinal: 3,
      role: "user",
      content: "The host affected was SRV-PROD-01.",
      retrieval_context_id: null,
      metadata_json: { evidence_kind: "clarification_answer" },
      created_at: "2026-08-23T10:10:00Z",
    };

    const assistantAnalysisMsg: PersistedChatMessage = {
      id: "msg-asst-4",
      thread_id: "thread-1",
      ordinal: 4,
      role: "assistant",
      content: `### 1. Overall Case Picture\nIncident analysis.`,
      retrieval_context_id: "rc-1",
      metadata_json: {
        analysis_kind: "grounded_main_analysis",
        analysis_trace: {
          version: "analysis_trace_v2",
          validation_status: "validated",
          analysis_mode: "case_overview",
          retrieval_context_id: "rc-1",
          evidence_sha256: "b".repeat(64),
          claims: [
            {
              claim_id: "A-01",
              claim_type: "reported",
              text: "Initial incident",
              epistemic_status: "reported",
              source_message_ids: ["msg-user-1"],
            },
            {
              claim_id: "A-02",
              claim_type: "reported",
              text: "Claim linking to analyst question and non-existent message",
              epistemic_status: "reported",
              source_message_ids: ["msg-user-2", "msg-nonexistent-99"],
            },
            {
              claim_id: "A-03",
              claim_type: "reported",
              text: "Clarification fact",
              epistemic_status: "reported",
              source_message_ids: ["msg-user-3"],
            },
          ],
          mitre_associations: [],
        },
        mitre_table: [],
      },
      created_at: "2026-08-23T10:15:00Z",
    };

    const overview = buildCaseOverview(
      [userMsg1, analystQuestionMsg, clarificationAnswerMsg, assistantAnalysisMsg],
      "answered",
    );

    // Claim A-01: valid initial description
    expect(overview.attackStory[0].sourceMessages).toHaveLength(1);
    expect(overview.attackStory[0].sourceMessages[0].label).toBe("Case description");
    expect(overview.attackStory[0].sourceMessages[0].sourceType).toBe("case_description");

    // Claim A-02: analyst_question and nonexistent ID must be completely excluded
    expect(overview.attackStory[1].sourceMessages).toHaveLength(0);

    // Claim A-03: clarification answer
    expect(overview.attackStory[2].sourceMessages).toHaveLength(1);
    expect(overview.attackStory[2].sourceMessages[0].label).toBe("Clarification");
    expect(overview.attackStory[2].sourceMessages[0].sourceType).toBe("clarification_response");
  });
});
