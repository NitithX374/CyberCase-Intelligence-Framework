import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";

describe("CaseOverviewView component", () => {
  it("renders empty state when no messages are provided", () => {
    const handleOpenChat = vi.fn();
    const handleOpenReport = vi.fn();

    render(
      <CaseOverviewView
        threadId="thread-1"
        threadTitle="Test Investigation"
        threadStatus="idle"
        messages={[]}
        onOpenChat={handleOpenChat}
        onOpenReport={handleOpenReport}
      />,
    );

    expect(screen.getByText(/No Case Activity Yet/i)).toBeInTheDocument();
    const btn = screen.getByRole("button", { name: /Go to Chat Workspace/i });
    fireEvent.click(btn);
    expect(handleOpenChat).toHaveBeenCalledTimes(1);
  });

  it("renders unanalysed state when messages exist but analysis is not complete", () => {
    const handleOpenChat = vi.fn();
    const handleOpenReport = vi.fn();
    const userMsg: PersistedChatMessage = {
      id: "msg-1",
      thread_id: "thread-1",
      ordinal: 1,
      role: "user",
      content: "Security incident reported.",
      retrieval_context_id: null,
      metadata_json: {},
      created_at: "2026-08-23T10:00:00Z",
    };

    render(
      <CaseOverviewView
        threadId="thread-1"
        threadTitle="Test Incident"
        threadStatus="idle"
        messages={[userMsg]}
        onOpenChat={handleOpenChat}
        onOpenReport={handleOpenReport}
      />,
    );

    expect(screen.getByText(/Analysis Required/i)).toBeInTheDocument();
    const btn = screen.getByRole("button", { name: /Open Chat/i });
    fireEvent.click(btn);
    expect(handleOpenChat).toHaveBeenCalledTimes(1);
  });

  it("renders full prosecutor overview with all 6 sections and interactive actions", () => {
    const handleOpenChat = vi.fn();
    const handleOpenReport = vi.fn();
    const handleNavigateToSource = vi.fn();

    const userMsg: PersistedChatMessage = {
      id: "msg-1",
      thread_id: "thread-1",
      ordinal: 1,
      role: "user",
      content: "Public IIS server compromised. Malicious scheduled task created.",
      retrieval_context_id: null,
      metadata_json: {},
      created_at: "2026-08-23T10:00:00Z",
    };

    const assistantMsg: PersistedChatMessage = {
      id: "msg-2",
      thread_id: "thread-1",
      ordinal: 2,
      role: "assistant",
      content: `### 1. Overall Case Picture (ภาพรวมคดี)
The attacker compromised the public web server and created scheduled tasks to maintain unauthorized persistence.

### 2. Key Sequence and Relationships
1. Access gained to IIS server.
2. Scheduled task deployed.

### 3. Relevant MITRE ATT&CK Context
Technique T1053.005 Scheduled Task.

### 4. Unresolved or Conflicting Information
Whether credentials were stolen from LSASS remains unconfirmed.

### 5. Analytical Boundary
Boundary observations.`,
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
              text: "Public IIS server was compromised.",
              epistemic_status: "reported",
              source_message_ids: ["msg-1"],
            },
            {
              claim_id: "A-02",
              claim_type: "reported",
              text: "Malicious scheduled task was created.",
              epistemic_status: "reported",
              source_message_ids: ["msg-1"],
            },
          ],
          mitre_associations: [
            {
              association_id: "MA-01",
              technique_id: "T1053.005",
              claim_ids: ["A-02"],
              reason: "Scheduled Task was configured for automatic task execution.",
              status: "candidate_only",
              support_role: "external_technical_context",
            },
          ],
        },
        mitre_table: [
          {
            technique_id: "T1053.005",
            name: "Scheduled Task",
            description: "Adversaries may abuse the Windows Task Scheduler to execute programs at system startup or on a scheduled basis.",
            tactic: "Execution",
          },
        ],
        chat_followup: {
          gap_analysis: {
            gaps: [
              {
                topic: "Privilege Escalation Vector",
                status: "NOT_PROVIDED",
                description: "Method used to elevate privileges was not documented.",
                affects: "Determining full impact",
                reason: "System audit logs missing.",
                priority: "medium",
                askable: true,
              },
            ],
          },
        },
      },
      created_at: "2026-08-23T10:01:00Z",
    };

    render(
      <CaseOverviewView
        threadId="thread-1"
        threadTitle="Cyber Incident Report Alpha"
        threadStatus="answered"
        messages={[userMsg, assistantMsg]}
        onOpenChat={handleOpenChat}
        onOpenReport={handleOpenReport}
        onNavigateToSource={handleNavigateToSource}
      />,
    );

    // Header checks
    expect(screen.getByText(/Prosecutor Case Overview/i)).toBeInTheDocument();
    expect(screen.getByText("Cyber Incident Report Alpha")).toBeInTheDocument();

    // Section 1: What Happened
    expect(screen.getByRole("heading", { name: /What Happened\?/i })).toBeInTheDocument();
    expect(screen.getByText(/The attacker compromised the public web server/i)).toBeInTheDocument();

    // Section 2: Attack Story & Progression
    expect(screen.getByRole("heading", { name: /Attack Story & Progression/i })).toBeInTheDocument();
    expect(screen.getAllByText("Public IIS server was compromised.").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Malicious scheduled task was created.").length).toBeGreaterThanOrEqual(1);

    // Section 3: What is Established?
    expect(screen.getByRole("heading", { name: /What is Established\?/i })).toBeInTheDocument();

    // Section 4: What Remains Unclear?
    expect(screen.getByRole("heading", { name: /What Remains Unclear\?/i })).toBeInTheDocument();
    expect(screen.getAllByText(/Method used to elevate privileges was not documented/i).length).toBeGreaterThanOrEqual(1);

    // Section 5: Relevant MITRE ATT&CK Context
    expect(screen.getByRole("heading", { name: /Relevant MITRE ATT&CK Context Explained/i })).toBeInTheDocument();
    expect(screen.getAllByText("Scheduled Task").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Trust Boundary Notice/i)).toBeInTheDocument();

    // Section 6: Points for Further Investigation
    expect(screen.getByRole("heading", { name: /Points for Further Investigation/i })).toBeInTheDocument();

    // Interactive CTAs
    const askButtons = screen.getAllByRole("button", { name: /Ask about this case/i });
    expect(askButtons.length).toBeGreaterThanOrEqual(1);
    fireEvent.click(askButtons[0]);
    expect(handleOpenChat).toHaveBeenCalled();

    const reportButtons = screen.getAllByRole("button", { name: /View Report|Generate \/ View Report/i });
    expect(reportButtons.length).toBeGreaterThanOrEqual(1);
    fireEvent.click(reportButtons[0]);
    expect(handleOpenReport).toHaveBeenCalled();

    // Source popover interaction
    const sourceBtns = screen.getAllByRole("button", { name: /Case description/i });
    expect(sourceBtns.length).toBeGreaterThanOrEqual(2);
    expect(sourceBtns[0]).toHaveAttribute("aria-expanded", "false");
    expect(sourceBtns[1]).toHaveAttribute("aria-expanded", "false");

    // Clicking first button activates ONLY first button
    fireEvent.click(sourceBtns[0]);
    expect(sourceBtns[0]).toHaveAttribute("aria-expanded", "true");
    expect(sourceBtns[1]).toHaveAttribute("aria-expanded", "false");
    expect(screen.getByText(/SOURCE FROM CASE/i)).toBeInTheDocument();
    expect(screen.getByText("Case description · รายละเอียดคดีเริ่มต้น")).toBeInTheDocument();
    expect(screen.getByText(/Public IIS server compromised. Malicious scheduled task created./i)).toBeInTheDocument();

    // Clicking second button switches active state to ONLY second button
    fireEvent.click(sourceBtns[1]);
    expect(sourceBtns[0]).toHaveAttribute("aria-expanded", "false");
    expect(sourceBtns[1]).toHaveAttribute("aria-expanded", "true");

    const viewInChatBtn = screen.getByRole("button", { name: /View in Chat/i });
    fireEvent.click(viewInChatBtn);
    expect(handleNavigateToSource).toHaveBeenCalledWith("msg-1");
  });
});
