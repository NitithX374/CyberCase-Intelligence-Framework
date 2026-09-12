import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { sourceMessage, analysisMessage } from "./overview-fixtures";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
import type { CaseRunRead } from "@/lib/api";
import { sha256Hex } from "@/lib/sha256";
import { mockNativeDialog } from "./mock-native-dialog";

mockNativeDialog();

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
    expect(screen.queryByRole("region", { name: "Case at a glance" })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Executive Summary/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Case Findings/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /^Contradicted/ })).toBeInTheDocument();
    expect(screen.getByText("Analytical inference")).toBeInTheDocument();
    expect(screen.queryByText(/does not independently verify it/i)).not.toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /^Source ·/ })).toHaveLength(3);
    expect(screen.getByRole("button", { name: /^Conflicting source ·/ })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /Open Questions/i })).toBeInTheDocument();
    expect(screen.getByText(/Needs clarification/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Clarify in Chat/ })).toBeInTheDocument();
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
    fireEvent.click(screen.getByRole("button", { name: /View in Materials/i }));
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

  it("puts a validated page citation directly below its finding", () => {
    const content = "Page 4: received 52,000 baht.";
    const source = sourceMessage("source-1", 1, content);
    source.metadata_json.document_sources = [{
      document_id: "DOC-1",
      filename: "statement.pdf",
      page_count: 4,
      page_spans: [{
        page_number: 4,
        start_offset: 0,
        end_offset: content.length,
        text_sha256: sha256Hex(content),
      }],
    }];
    const analysis = analysisMessage(false);
    analysis.metadata_json.analysis_trace = {
      ...(analysis.metadata_json.analysis_trace as Record<string, unknown>),
      claims: [{
        claim_id: "A-01",
        claim_type: "reported",
        text: "The submitted material reports a receipt.",
        epistemic_status: "reported",
        supporting_source_message_ids: ["source-1"],
        contradicting_source_message_ids: [],
        supporting_citations: [{
          source_message_id: "source-1",
          exact_quote: "received 52,000 baht",
          document_id: "DOC-1",
          filename: "statement.pdf",
          page_numbers: [4],
        }],
        contradicting_citations: [],
        reasoning_summary: null,
      }],
    };

    render(
      <CaseOverviewView
        threadId="thread-1"
        threadTitle="Receipt Review"
        threadStatus="answered"
        messages={[source, analysis]}
        onOpenChat={vi.fn()}
        onOpenReport={vi.fn()}
      />,
    );

    const pageCitations = screen.getAllByRole("button", { name: "Source · statement.pdf · p. 4" });
    expect(pageCitations).toHaveLength(1);
    expect(screen.queryByText("Reported in case material")).not.toBeInTheDocument();
    fireEvent.click(pageCitations[0]);
    expect(screen.getByRole("dialog")).toHaveTextContent("Page 4");
    expect(screen.getByRole("dialog")).toHaveTextContent("received 52,000 baht");
    expect(screen.getByRole("dialog").querySelector("mark")).toHaveTextContent("received 52,000 baht");
    fireEvent.click(screen.getByRole("button", { name: "Close source evidence" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(pageCitations[0]).toHaveFocus();
  });

  it("closes narrative inspection on native dialog cancel without inventing a document page", () => {
    render(<CaseOverviewView threadId="thread-1" threadTitle="Narrative review" threadStatus="answered"
      messages={[sourceMessage("source-1", 1, "Original statement"), analysisMessage(false)]}
      onOpenChat={vi.fn()} onOpenReport={vi.fn()} />);
    const sourceButton = screen.getAllByRole("button", { name: "Source · Case narrative" })[0];
    fireEvent.click(sourceButton);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveTextContent("Original statement");
    expect(dialog).not.toHaveTextContent(/Page \d|\.pdf/);
    fireEvent(dialog, new Event("cancel", { bubbles: false, cancelable: true }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(sourceButton).toHaveFocus();
  });

  it("renders failed state when native run has failed and no analysis result is present", () => {
    const openIntake = vi.fn();
    render(
      <CaseOverviewView
        threadId="case-1"
        threadTitle="Failed Case"
        threadStatus="idle"
        messages={[]}
        onOpenChat={vi.fn()}
        onOpenReport={vi.fn()}
        onOpenIntake={openIntake}
        nativeRunStatus="failed"
        nativeRun={{
          id: "run-1",
          case_id: "case-1",
          status: "failed",
          error_message: "Case analysis extraction failed.",
          created_at: "2026-09-10T00:00:00Z",
          updated_at: "2026-09-10T00:00:00Z",
        } as unknown as CaseRunRead}
      />,
    );
    expect(screen.getByText("Analysis Failed")).toBeInTheDocument();
    expect(screen.getByText("Case analysis extraction failed.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Open Intake" }));
    expect(openIntake).toHaveBeenCalledOnce();
  });

  it("renders clarification needed state with Proceed to Chat button when a clarification is pending", () => {
    const openChat = vi.fn();
    const clarification = {
      id: "clarification-1",
      case_id: "case-1",
      origin_analysis_result_id: "analysis-1",
      origin_snapshot_id: "snapshot-1",
      gap_key: "topic:incident-time",
      gap_id: "G-01",
      topic: "Incident time",
      question: "When did the incident occur?",
      metadata_json: {},
      state: "pending" as const,
      answer_evidence_source_id: null,
      question_message_id: null,
      answer_message_id: null,
      answer_fingerprint: null,
      answered_at: null,
      created_at: "2026-09-10T01:00:00Z",
      updated_at: "2026-09-10T01:00:00Z",
    };

    render(
      <CaseOverviewView
        threadId="case-1"
        threadTitle="Awaiting Case"
        threadStatus="awaiting_followup"
        messages={[]}
        onOpenChat={openChat}
        onOpenReport={vi.fn()}
        nativeClarifications={[clarification]}
      />,
    );

    expect(screen.getByText(/CLARIFICATION NEEDED/i)).toBeInTheDocument();
    expect(screen.getByText("Analysis Needs More Information")).toBeInTheDocument();
    expect(screen.getByText(/When did the incident occur\?/)).toBeInTheDocument();
    expect(screen.queryByText(/Executive Summary/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Case Findings/i)).not.toBeInTheDocument();

    const proceedButton = screen.getByRole("button", { name: "Proceed to Chat" });
    expect(proceedButton).toBeInTheDocument();
    fireEvent.click(proceedButton);
    expect(openChat).toHaveBeenCalledOnce();
  });

  it("renders stale analysis warning with Analyze latest evidence button when freshness is stale", () => {
    const runAnalysis = vi.fn();
    const staleResult = {
      id: "analysis-stale",
      case_id: "case-1",
      run_id: "run-1",
      snapshot_id: "snapshot-1",
      schema_version: "v1",
      status: "validated" as const,
      answer: "Old analysis.",
      summary: "Old summary.",
      trace_json: {
        version: "case_analysis_trace_v1",
        validation_status: "validated",
        analysis_mode: "case_overview",
        evidence_sha256: "sha",
        summary: "Old summary.",
        claims: [],
        gaps: [],
        mitre_associations: [],
      },
      execution_receipt_json: {},
      retrieval_context_id: null,
      pipeline_config: {},
      provider_metadata_json: {},
      created_at: "2026-09-10T00:00:00Z",
      freshness: "stale" as const,
    };
    const sourceId = "11111111-1111-4111-8111-111111111111";
    const quote = "The suspect vehicle was observed at 14:32.";
    const manifest = [{
      exact_text: quote,
      provenance: { origin: "analyst-authored" },
      revision: 1,
      source_id: sourceId,
      source_kind: "narrative",
      text_sha256: sha256Hex(quote),
    }];
    const inputText = `[CASE NARRATIVE · SOURCE ${sourceId} · REVISION 1]\n${quote}`;
    const textSha = sha256Hex(inputText);
    staleResult.trace_json.evidence_sha256 = textSha;
    const snapshot = {
      id: "snapshot-1",
      case_id: "case-1",
      evidence_revision: 1,
      format_version: "case_evidence_snapshot_v1",
      input_text: inputText,
      text_sha256: textSha,
      manifest_sha256: sha256Hex(JSON.stringify(manifest)),
      manifest_json: manifest,
      created_at: "2026-09-10T00:00:00Z",
    };

    render(
      <CaseOverviewView
        threadId="case-1"
        threadTitle="Stale Case"
        threadStatus="answered"
        messages={[]}
        onOpenChat={vi.fn()}
        onOpenReport={vi.fn()}
        nativeAnalysisResult={staleResult}
        nativeEvidenceSnapshot={snapshot}
        onRunAnalysis={runAnalysis}
      />,
    );

    expect(
      screen.getByText(/Analysis is based on older evidence/i),
    ).toBeInTheDocument();
    const analyzeBtn = screen.getByRole("button", {
      name: /Analyze latest evidence/i,
    });
    expect(analyzeBtn).toBeInTheDocument();
    fireEvent.click(analyzeBtn);
    expect(runAnalysis).toHaveBeenCalledOnce();
  });
});
