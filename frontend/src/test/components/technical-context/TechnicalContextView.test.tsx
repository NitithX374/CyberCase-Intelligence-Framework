import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TechnicalContextView } from "@/components/technical-context/TechnicalContextView";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api";
import { mockNativeDialog } from "../overview/mock-native-dialog";

mockNativeDialog();

const caseId = "22222222-2222-4222-8222-222222222222";
const sourceId = "11111111-1111-4111-8111-111111111111";
const exactQuote = "The report records PowerShell network activity.";

function technicalProjection(): { result: CaseAnalysisResultRead; sources: CaseSourceRead[] } {
  const sources: CaseSourceRead[] = [
    {
      id: sourceId,
      case_id: caseId,
      source_kind: "narrative",
      document_id: null,
      origin_message_id: null,
      exact_text: exactQuote,
      provenance_json: {},
      source_metadata_json: {},
      created_at: "2026-09-10T00:00:00Z",
      archived_at: null,
    },
  ];
  const result: CaseAnalysisResultRead = {
    id: "44444444-4444-4444-8444-444444444444",
    case_id: caseId,
    source_revision: 1,
    schema_version: "case_analysis_trace_v1",
    status: "validated",
    answer: exactQuote,
    summary: exactQuote,
    trace_json: {
      version: "case_analysis_trace_v1",
      validation_status: "validated",
      analysis_mode: "case_overview",
      summary: exactQuote,
      claims: [
        {
          claim_id: "A-01",
          claim_type: "reported",
          text: exactQuote,
          epistemic_status: "reported",
          reasoning_summary: null,
          supporting_source_ids: [sourceId],
          contradicting_source_ids: [],
          supporting_citations: [{ source_id: sourceId, exact_quote: exactQuote }],
          contradicting_citations: [],
        },
      ],
      gaps: [],
      mitre_associations: [
        {
          association_id: "MA-01",
          technique_id: "T1059.001",
          claim_ids: ["A-01"],
          reason: "The claim describes PowerShell activity.",
          plain_meaning: "Someone ran commands through PowerShell.",
          status: "candidate_only",
          support_role: "external_technical_context",
        },
      ],
      retrieval_context_id: "retrieval-1",
    },
    retrieval_context_id: "retrieval-1",
    pipeline_config: {},
    external_context_json: {
      technical_augmentation: {
        version: "case_mitre_augmentation_v1",
        status: "retrieved_with_matches",
        applicability: {
          decision: "RETRIEVE",
          source_message_ids: [sourceId],
          trigger_text: [exactQuote],
        },
        retrieval_context_id: "retrieval-1",
        mitre_table: [
          {
            technique_id: "T1059.001",
            name: "PowerShell",
            tactic: "Execution",
            description: "Command and scripting interpreter.",
            source: "vector",
            score: 0.93,
          },
        ],
        association_ids: ["MA-01"],
      },
    },
    created_at: "2026-09-10T12:00:00Z",
    freshness: "current",
  };
  return { result, sources };
}

describe("TechnicalContextView", () => {
  it("shows the optional-context empty state without Case analysis", () => {
    const openSources = vi.fn();
    render(
      <TechnicalContextView analysisResult={null} sources={null} onOpenSources={openSources} />,
    );
    expect(
      screen.getByText("No ATT&CK context is available for this analysis."),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Go to sources/i }));
    expect(openSources).toHaveBeenCalledOnce();
  });

  it("shows validated Case mappings and inspects their exact source", () => {
    const projection = technicalProjection();
    const navigateToSource = vi.fn();
    render(
      <TechnicalContextView
        analysisResult={projection.result}
        sources={projection.sources}
        onNavigateToSource={navigateToSource}
      />,
    );
    expect(screen.getByRole("heading", { name: "PowerShell" })).toBeInTheDocument();
    // The card quotes the sentence it rests on, and says how firmly.
    expect(screen.getByText(`“${exactQuote}”`)).toBeInTheDocument();
    // The number comes from the retriever, not from the model rating itself.
    expect(screen.getByText("Retrieval match")).toBeInTheDocument();
    expect(screen.getByText("0.93")).toBeInTheDocument();
    expect(screen.getByText("Someone ran commands through PowerShell.")).toBeInTheDocument();
    // Why the technique fits this case is one step away, not on the card.
    expect(screen.queryByText("The claim describes PowerShell activity.")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Why it applies" }));
    expect(screen.getByText("The claim describes PowerShell activity.")).toBeInTheDocument();
    const source = screen.getByRole("button", { name: new RegExp(exactQuote.slice(0, 20), "i") });
    fireEvent.click(source);
    expect(screen.getByRole("dialog")).toHaveTextContent(exactQuote);
    fireEvent.click(screen.getByRole("button", { name: /Open in Sources/i }));
    expect(navigateToSource).toHaveBeenCalledWith(sourceId);
  });

  it("keeps a non-technical Case valid without MITRE rows", () => {
    const projection = technicalProjection();
    projection.result.trace_json = {
      ...projection.result.trace_json!,
      mitre_associations: [],
      retrieval_context_id: null,
    };
    projection.result.retrieval_context_id = null;
    projection.result.external_context_json = {
      technical_augmentation: {
        version: "case_mitre_augmentation_v1",
        status: "not_applicable",
        applicability: { decision: "SKIP", source_message_ids: [], trigger_text: [] },
        retrieval_context_id: null,
        mitre_table: [],
        association_ids: [],
      },
    };
    render(
      <TechnicalContextView analysisResult={projection.result} sources={projection.sources} />,
    );
    expect(
      screen.getByText("Not applicable — the case has no technical indicators."),
    ).toBeInTheDocument();
    expect(screen.queryByText("PowerShell")).not.toBeInTheDocument();
  });
});
