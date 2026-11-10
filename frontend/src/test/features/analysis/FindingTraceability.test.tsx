import { useState } from "react";
import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { CaseAnalysisResultRead, CaseSourceRead } from "@/lib/api/types";
import type { SourceMessageRef } from "@/features/citations/types";
import { SourceDrawer } from "@/features/citations/SourceDrawer";
import { CaseFindingsSection } from "@/features/analysis/CaseFindingsSection";
import { buildCaseOverview } from "@/features/analysis/overview";
import { analysisResult, caseId, claim, pagedDocumentSource, trace } from "@/test/fixtures";

const first = "John sent an email.";
const second = "The company received it on Monday.";
const source = pagedDocumentSource(`${first} ${second}`, 1);
const reading = analysisResult({
  trace_json: trace({
    claims: [
      claim("John sent an email that the company received on Monday.", source.id, {
        supporting_citations: [
          {
            source_id: source.id,
            exact_quote: first,
            pointer_state: "direct",
            evidence_unit_ids: [`${source.id}:U001-revision`],
            start: 0,
            end: first.length,
            page_numbers: [1],
          },
          {
            source_id: source.id,
            exact_quote: second,
            pointer_state: "direct",
            evidence_unit_ids: [`${source.id}:U002-revision`],
            start: first.length + 1,
            end: source.exact_text.length,
            page_numbers: [1],
          },
        ],
      }),
    ],
  }),
});

function Findings({
  result = reading,
  rows = [source],
}: {
  result?: CaseAnalysisResultRead;
  rows?: CaseSourceRead[];
}) {
  const [selected, setSelected] = useState<{
    sourceRef: SourceMessageRef;
    anchorElement: HTMLElement;
    citationRole?: "supporting" | "conflicting";
  } | null>(null);
  const overview = buildCaseOverview(result, rows);
  return (
    <>
      <CaseFindingsSection
        caseId={caseId}
        findings={overview.findings}
        onSelectSource={(sourceRef, anchorElement, _key, citationRole) =>
          setSelected({ sourceRef, anchorElement, citationRole })
        }
      />
      {selected && <SourceDrawer {...selected} onClose={() => setSelected(null)} />}
    </>
  );
}

function markedText(): string[] {
  return Array.from(screen.getByRole("dialog").querySelectorAll("mark"), (mark) =>
    (mark.textContent ?? "").trim(),
  );
}

describe("Finding traceability", () => {
  it.each([
    [
      "not_supported",
      "lr_not_supported",
      "Source check: the cited Source did not clearly support this finding. Check it before relying on it.",
    ],
    [
      "unassessed",
      "no_resolved_source",
      "Support could not be assessed, so it was left out of the summary.",
    ],
    ["unassessed", "verifier_unavailable", "Source check unavailable. Not assessed."],
  ] as const)(
    "shows the saved semantic verdict %s independently of Source binding",
    (verdict, reason, label) => {
      const result = structuredClone(reading);
      result.trace_json!.claims[0].semantic_grounding = {
        verdict,
        reason,
      };
      render(<Findings result={result} />);
      expect(screen.getByText(label)).toBeVisible();
      expect(screen.queryByText(/directly linked passage/)).not.toBeInTheDocument();
      expect(screen.queryByText("Support not checked")).not.toBeInTheDocument();
    },
  );

  it("gives a supported finding no check mark, support sentence or styling of its own", () => {
    const result = structuredClone(reading);
    const unflagged = structuredClone(result.trace_json!.claims[0]);
    unflagged.claim_id = "A-02";
    unflagged.semantic_grounding = null;
    result.trace_json!.claims[0].semantic_grounding = {
      verdict: "supported",
      reason: "lr_supported",
    };
    result.trace_json!.claims.push(unflagged);
    const { container } = render(<Findings result={result} />);

    const [supported, other] = screen.getAllByRole("article");
    expect(supported.className).toBe(other.className);
    expect(supported.firstElementChild!.className).toBe(other.firstElementChild!.className);
    expect(within(supported).queryByLabelText("Finding traceability")).not.toBeInTheDocument();
    expect(within(other).getByLabelText("Finding traceability")).toBeInTheDocument();
    expect(supported.querySelectorAll("svg")).toHaveLength(other.querySelectorAll("svg").length);
    expect(supported).not.toHaveTextContent(/support/i);
    expect(container.innerHTML).not.toMatch(/established|accent-soft/);
  });

  it("keeps the warning for a finding the verifier did not clearly support", () => {
    const result = structuredClone(reading);
    result.trace_json!.claims[0].semantic_grounding = {
      verdict: "not_supported",
      reason: "lr_not_supported",
    };
    render(<Findings result={result} />);

    expect(
      screen.getByText(
        "Source check: the cited Source did not clearly support this finding. Check it before relying on it.",
      ),
    ).toHaveClass("text-unresolved");
  });

  it("opens every cited passage from the same Source and page using one chip", () => {
    render(<Findings />);
    const chips = screen.getAllByRole("button", { name: /statement\.pdf/ });
    expect(chips).toHaveLength(1);
    expect(chips[0]).toHaveAccessibleName("statement.pdf · p. 1 · 2 passages");
    fireEvent.click(chips[0]);
    expect(markedText()).toEqual([first, second]);
    expect(screen.getByRole("dialog")).not.toHaveTextContent("U001-revision");
    expect(screen.getByRole("dialog")).not.toHaveTextContent("U002-revision");
  });

  it("shows semantic support without inventing confidence", () => {
    const { container } = render(<Findings />);
    expect(screen.queryByText(/directly linked passage/)).not.toBeInTheDocument();
    expect(screen.getByText("Support not checked")).toBeVisible();
    expect(container.textContent).not.toMatch(
      /\b\d+(?:\.\d+)?%|semantically verified|confirmed true/i,
    );
  });

  it("does not infer Source linkage from an old not-confirmed claim status", () => {
    const result = structuredClone(reading);
    result.trace_json!.claims[0].epistemic_status = "not_confirmed";
    render(<Findings result={result} />);
    expect(screen.queryByText(/directly linked passage/)).not.toBeInTheDocument();
    expect(screen.getByText("Support not checked")).toBeVisible();
    expect(screen.queryByText("No linked supporting Source passage")).not.toBeInTheDocument();
  });

  it("explains unknown Source pointers without claiming a quote comparison failed", () => {
    const result = analysisResult({
      trace_json: trace({
        claims: [
          claim("John sent an email.", source.id, {
            epistemic_status: "not_confirmed",
            supporting_citations: [],
            invalid_evidence: [
              {
                source_id: "missing-source",
                evidence_unit_id: "missing-source:U001-revision",
                role: "supporting",
                pointer_state: "unresolved",
                reason: "unknown_source",
              },
            ],
          }),
        ],
      }),
    });
    render(<Findings result={result} />);
    expect(screen.queryByText(/unresolved reference/)).not.toBeInTheDocument();
    expect(screen.queryByText("No linked supporting Source passage")).not.toBeInTheDocument();
    expect(screen.getByText("Support not checked")).toBeVisible();
    expect(screen.queryByText("Not found word for word in the source.")).not.toBeInTheDocument();
  });

  it("shows Thai status text while keeping all cited Thai fragments visible", () => {
    const firstThai = "จอห์นส่งอีเมลถึงบริษัท";
    const secondThai = "บริษัทได้รับอีเมลในวันจันทร์";
    const thaiSource = pagedDocumentSource(`${firstThai}\n${secondThai}`, 1);
    const result = analysisResult({
      trace_json: trace({
        claims: [
          claim(`${firstThai} และ${secondThai}`, thaiSource.id, {
            supporting_citations: [
              {
                source_id: thaiSource.id,
                exact_quote: firstThai,
                pointer_state: "direct",
                start: 0,
                end: Array.from(firstThai).length,
                page_numbers: [1],
              },
              {
                source_id: thaiSource.id,
                exact_quote: secondThai,
                pointer_state: "recovered",
                page_numbers: [1],
              },
            ],
          }),
        ],
      }),
    });
    render(<Findings result={result} rows={[thaiSource]} />);
    expect(screen.queryByText(/เชื่อม Source โดยตรง/)).not.toBeInTheDocument();
    expect(screen.queryByText(/ค้นคืนตำแหน่งใน Source/)).not.toBeInTheDocument();
    expect(screen.getByText("ยังไม่ได้ตรวจว่า Source รองรับข้อค้นพบนี้หรือไม่")).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: /statement\.pdf/ }));
    expect(markedText()).toEqual([firstThai, secondThai]);
  });

  it("keeps supporting and conflicting passages in separate drawers", () => {
    const result = analysisResult({
      trace_json: trace({
        claims: [
          claim(first, source.id, {
            supporting_citations: [
              {
                source_id: source.id,
                exact_quote: first,
                pointer_state: "direct",
                page_numbers: [1],
              },
            ],
            contradicting_source_ids: [source.id],
            contradicting_citations: [
              {
                source_id: source.id,
                exact_quote: second,
                pointer_state: "recovered",
                page_numbers: [1],
              },
            ],
          }),
        ],
      }),
    });
    render(<Findings result={result} />);
    expect(screen.queryByText(/directly linked passage/)).not.toBeInTheDocument();
    expect(screen.queryByText(/recovered passage/)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Conflicts with statement.pdf · p. 1" }));
    expect(markedText()).toEqual([second]);
    expect(screen.getByText("Conflicting source")).toBeVisible();
  });
});
