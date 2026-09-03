import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { sourceMessage, analysisMessage } from "./overview-fixtures";
import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
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
});
