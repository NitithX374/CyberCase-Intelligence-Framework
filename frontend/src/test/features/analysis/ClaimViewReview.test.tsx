import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseDetails } from "@/features/analysis/CaseDetails";
import { ProjectionReview } from "@/features/analysis/ProjectionReview";
import type { ClaimBacked } from "@/features/analysis/types";

describe("extracted claim view context", () => {
  it("does not equate a missed role with an absent role in the claim", () => {
    render(
      <CaseDetails
        parties={[
          {
            name: "Jane",
            role: null,
            sources: [],
            inferred: false,
            unconfirmed: [],
            fieldSpans: { name: { claim_id: "A-01", start: 0, end: 4 } },
            linkedClaims: [{ id: "A-01", text: "Jane is the complainant." }],
          },
        ]}
        timeline={[]}
        impacts={[]}
        onSelectSource={vi.fn()}
        activeSourceKey={null}
      />,
    );
    expect(screen.getByText("No role extracted; check the linked claim")).toBeInTheDocument();
    expect(screen.getByLabelText("Claim context")).toHaveTextContent("Jane is the complainant.");
  });

  it("keeps original attribution visible without implying a semantic check or Judgement admission", () => {
    const row: ClaimBacked = {
      sources: [],
      inferred: false,
      unconfirmed: [],
      fieldSpans: { name: { claim_id: "A-01", start: 35, end: 39 } },
      linkedClaims: [{ id: "A-01", text: "The complainant alleged that John sent an email." }],
    };
    render(<ProjectionReview row={row} caseId="case-1" />);
    expect(screen.getByText("Extracted from linked claims")).toBeInTheDocument();
    expect(screen.getByLabelText("Claim context")).toHaveTextContent("The complainant alleged");
    expect(screen.getByRole("link", { name: "A-01" })).toHaveAttribute(
      "href",
      "/case/case-1/analysis/findings?finding=A-01",
    );
    expect(screen.getByText(/no recorded semantic verification/)).toBeInTheDocument();
    expect(screen.queryByText(/earlier Judgement/)).not.toBeInTheDocument();
  });
});
