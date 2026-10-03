import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TechnicalContextView } from "@/features/analysis/technical-context/TechnicalContextView";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api/types";
import { analysisResult, association, claim, narrativeSource, trace } from "@/test/fixtures";

const exactQuote = "The report records PowerShell network activity.";

function technicalProjection(): { result: CaseAnalysisResultRead; sources: CaseSourceRead[] } {
  const result = analysisResult({
    summary: exactQuote,
    trace_json: trace({
      summary: exactQuote,
      claims: [claim(exactQuote)],
      mitre_associations: [
        association("T1059.001", {
          reason: "The claim describes PowerShell activity.",
          plain_meaning: "Someone ran commands through PowerShell.",
        }),
      ],
      retrieval_context_id: "retrieval-1",
    }),
    retrieval_context_id: "retrieval-1",
    external_context_json: {
      technical_augmentation: {
        version: "case_mitre_augmentation_v1",
        status: "retrieved_with_matches",
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
  });
  return { result, sources: [narrativeSource(exactQuote)] };
}

describe("TechnicalContextView", () => {
  it("shows validated Case mappings and inspects their exact source", () => {
    const projection = technicalProjection();
    render(
      <TechnicalContextView analysisResult={projection.result} sources={projection.sources} />,
    );
    expect(screen.getByRole("heading", { name: "PowerShell" })).toBeInTheDocument();
    expect(screen.getByText(`“${exactQuote}”`)).toBeInTheDocument();
    expect(screen.getByText("Match 0.93")).toBeInTheDocument();
    expect(screen.getByText("Someone ran commands through PowerShell.")).toBeInTheDocument();
    expect(screen.queryByText("The claim describes PowerShell activity.")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Why it applies" }));
    expect(screen.getByText("The claim describes PowerShell activity.")).toBeInTheDocument();
    const source = screen.getByRole("button", { name: new RegExp(exactQuote.slice(0, 20), "i") });
    fireEvent.click(source);
    expect(screen.getByRole("dialog")).toHaveTextContent(exactQuote);
  });

  it("says in words when a technique rests on no case source", () => {
    const projection = technicalProjection();
    const claim = projection.result.trace_json!.claims[0];
    claim.supporting_source_ids = [];
    claim.supporting_citations = [];
    render(
      <TechnicalContextView analysisResult={projection.result} sources={projection.sources} />,
    );
    expect(screen.getByRole("heading", { name: "PowerShell" })).toBeInTheDocument();
    expect(screen.getByText("No case source is recorded for this technique.")).toBeInTheDocument();
    expect(screen.queryByText(/could not be verified/)).not.toBeInTheDocument();
  });

  it("prints no quotation for a source with no checked quote, and never the start of the source", () => {
    const projection = technicalProjection();
    const unconfirmed = projection.result.trace_json!.claims[0];
    unconfirmed.epistemic_status = "not_confirmed";
    unconfirmed.supporting_citations = [];
    render(
      <TechnicalContextView analysisResult={projection.result} sources={projection.sources} />,
    );

    expect(screen.getByText("ไม่มี quote ที่ตรวจแล้ว")).toBeInTheDocument();
    expect(screen.queryByText(/“|”/)).not.toBeInTheDocument();
    expect(screen.queryByText(new RegExp(exactQuote.slice(0, 20)))).not.toBeInTheDocument();
    expect(screen.queryByText("No quotation recorded.")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Case narrative #1/ }));
    expect(screen.getByRole("dialog")).toHaveTextContent(exactQuote);
  });

  it("quotes only the sources whose quote was checked, beside one that was not", () => {
    const otherId = "33333333-3333-4333-8333-333333333333";
    const projection = technicalProjection();
    const other = "A second report places the attacker on the file server.";
    projection.result.trace_json!.claims.push({
      ...claim(other, otherId, { claim_id: "A-02" }),
      epistemic_status: "not_confirmed",
      supporting_citations: [],
    });
    projection.result.trace_json!.mitre_associations![0].claim_ids = ["A-01", "A-02"];
    projection.sources.push(narrativeSource(other, { id: otherId }));
    render(
      <TechnicalContextView analysisResult={projection.result} sources={projection.sources} />,
    );

    expect(screen.getByText(`“${exactQuote}”`)).toBeInTheDocument();
    expect(screen.getAllByText("ไม่มี quote ที่ตรวจแล้ว")).toHaveLength(1);
    expect(screen.queryByText(new RegExp(other.slice(0, 20)))).not.toBeInTheDocument();
    expect(screen.getByText("Case narrative #1")).toBeInTheDocument();
    expect(screen.getByText("Case narrative #2")).toBeInTheDocument();
  });

  it("keeps a non-technical Case valid without MITRE rows", () => {
    const projection = technicalProjection();
    projection.result.trace_json = {
      ...projection.result.trace_json!,
      mitre_associations: [],
      retrieval_context_id: null,
    };
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
