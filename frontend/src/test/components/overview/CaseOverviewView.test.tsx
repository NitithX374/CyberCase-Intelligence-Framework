import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";

function sourceMessage(id: string, ordinal: number, content: string): PersistedChatMessage {
  return {
    id,
    thread_id: "thread-1",
    ordinal,
    role: "user",
    content,
    retrieval_context_id: null,
    metadata_json: {
      evidence_kind: ordinal === 1 ? "initial_case_narrative" : "clarification_answer",
    },
    created_at: `2026-08-23T10:0${ordinal}:00Z`,
  };
}

function analysisMessage(cyber = true): PersistedChatMessage {
  return {
    id: "analysis-1",
    thread_id: "thread-1",
    ordinal: 3,
    role: "assistant",
    content: "Rendered narrative is separate from the structured trace.",
    retrieval_context_id: cyber ? "context-1" : null,
    metadata_json: {
      analysis_kind: "grounded_main_analysis",
      analysis_state_scope: "canonical_case_overview",
      analysis_trace: {
        version: "analysis_trace_v3",
        validation_status: "validated",
        analysis_mode: "case_overview",
        summary: "The case material contains conflicting recipient information.",
        claims: [
          {
            claim_id: "A-01",
            claim_type: "reported",
            text: "The reporting party named Account A.",
            epistemic_status: "contradicted",
            supporting_source_message_ids: ["source-1"],
            contradicting_source_message_ids: ["source-2"],
            reasoning_summary: null,
          },
          {
            claim_id: "A-02",
            claim_type: "analytical_inference",
            text: "The recipient identity is not established.",
            epistemic_status: "not_established",
            supporting_source_message_ids: ["source-1", "source-2"],
            contradicting_source_message_ids: [],
            reasoning_summary: "The submitted sources identify different accounts.",
          },
        ],
        gaps: [
          {
            gap_id: "G-01",
            topic: "Recipient identity",
            status: "CONFLICTING",
            description: "Current sources name different recipient accounts.",
            affected_claim_ids: ["A-01", "A-02"],
            reason: "No current source resolves the discrepancy.",
            priority: "high",
            askable: true,
          },
        ],
        mitre_associations: cyber
          ? [{
              association_id: "MA-01",
              technique_id: "T1566.002",
              claim_ids: ["A-02"],
              reason: "The submitted material mentions a suspicious link.",
              status: "candidate_only",
              support_role: "external_technical_context",
            }]
          : [],
        evidence_sha256: "b".repeat(64),
        retrieval_context_id: cyber ? "context-1" : null,
      },
      mitre_applicability: { decision: cyber ? "RETRIEVE" : "SKIP" },
      rag_attempt: { status: cyber ? "used" : "no_applicable_context" },
      mitre_table: cyber
        ? [{
            technique_id: "T1566.002",
            name: "Spearphishing Link",
            description: "A link may be used to gain access.",
          }]
        : [],
    },
    created_at: "2026-08-23T10:03:00Z",
  };
}

describe("CaseOverviewView", () => {
  it("renders a domain-neutral empty state", () => {
    const openChat = vi.fn();
    render(
      <CaseOverviewView
        threadId="thread-1"
        threadTitle="Test Case"
        threadStatus="idle"
        messages={[]}
        onOpenChat={openChat}
        onOpenReport={vi.fn()}
      />,
    );
    expect(screen.getByText("No Case Material Yet")).toBeInTheDocument();
    expect(screen.queryByText(/prosecutor|attack story/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Open Intake" }));
    expect(openChat).toHaveBeenCalledOnce();
  });

  it("renders truthful findings, separated sources, gaps, and optional cyber context", () => {
    const openChat = vi.fn();
    const openReport = vi.fn();
    const navigateToSource = vi.fn();
    const messages = [
      sourceMessage("source-1", 1, "The reporting party named Account A."),
      sourceMessage("source-2", 2, "The bank record names Account B."),
      analysisMessage(),
    ];
    render(
      <CaseOverviewView
        threadId="thread-1"
        threadTitle="Transfer Review"
        threadStatus="answered"
        messages={messages}
        onOpenChat={openChat}
        onOpenReport={openReport}
        onNavigateToSource={navigateToSource}
      />,
    );

    expect(screen.getByText("Transfer Review")).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Case at a glance" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /What the Case Currently Says/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Case Findings/i })).toBeInTheDocument();
    expect(screen.getByText("Conflicting evidence")).toBeInTheDocument();
    expect(screen.getByText("Analytical inference")).toBeInTheDocument();
    expect(screen.getByText(/does not independently verify it/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Supporting case sources/i)).toHaveLength(2);
    expect(screen.getByText(/Conflicting case sources/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Open Questions/i })).toBeInTheDocument();
    expect(screen.getByText("Needs clarification")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Clarify in Chat" })).toBeInTheDocument();
    expect(screen.queryByText("A-01", { exact: true })).not.toBeInTheDocument();
    expect(screen.queryByText("G-01", { exact: true })).not.toBeInTheDocument();
    expect(screen.queryByText("high", { exact: true })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /External Cyber Reference/i })).toBeInTheDocument();
    expect(screen.getAllByText(/Spearphishing Link/i).length).toBeGreaterThan(0);
    expect(screen.queryByRole("heading", { name: /Attack Story/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /What is Established/i })).not.toBeInTheDocument();

    const sourceButtons = screen.getAllByRole("button", { name: /Case narrative/i });
    fireEvent.click(sourceButtons[0]);
    expect(screen.getByRole("dialog", { name: /Source Evidence/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /View in Chat/i }));
    expect(navigateToSource).toHaveBeenCalledWith("source-1");
    fireEvent.click(screen.getByRole("button", { name: "Ask about this case" }));
    expect(openChat).toHaveBeenCalledOnce();
    fireEvent.click(screen.getByRole("button", { name: "View Report" }));
    expect(openReport).toHaveBeenCalledOnce();
  });

  it("does not render MITRE labels for a non-cyber case", () => {
    render(
      <CaseOverviewView
        threadId="thread-1"
        threadTitle="General Case"
        threadStatus="answered"
        messages={[
          sourceMessage("source-1", 1, "Statement A"),
          sourceMessage("source-2", 2, "Statement B"),
          analysisMessage(false),
        ]}
        onOpenChat={vi.fn()}
        onOpenReport={vi.fn()}
      />,
    );
    expect(screen.queryByText(/MITRE ATT&CK/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /External Cyber Reference/i })).not.toBeInTheDocument();
  });
});
