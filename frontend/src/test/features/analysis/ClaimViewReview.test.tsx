import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseDetails } from "@/features/analysis/CaseDetails";
import { ClaimViewReview } from "@/features/analysis/ClaimViewReview";
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
    fireEvent.click(screen.getByText("Related findings"));
    expect(screen.getByLabelText("Related findings")).toHaveTextContent("Jane is the complainant.");
  });

  it("keeps original attribution visible without implying a semantic check or Judgement admission", () => {
    const row: ClaimBacked = {
      sources: [],
      inferred: false,
      unconfirmed: [],
      linkedClaims: [{ id: "A-01", text: "The complainant alleged that John sent an email." }],
    };
    const { container } = render(<ClaimViewReview row={row} caseId="case-1" />);
    expect(container.querySelector("details")).not.toHaveAttribute("open");
    fireEvent.click(screen.getByText("Related findings"));
    expect(screen.getByLabelText("Related findings")).toHaveTextContent("The complainant alleged");
    expect(screen.getByRole("link", { name: "View finding" })).toHaveAttribute(
      "href",
      "/case/case-1/analysis/findings?finding=A-01",
    );
    expect(container.textContent).not.toMatch(/A-01|semantic verification|earlier Judgement/);
    expect(screen.queryByText(/earlier Judgement/)).not.toBeInTheDocument();
  });

  it("links LLM views to Claims without invented offsets or historical admission labels", () => {
    const row: ClaimBacked = {
      sources: [],
      inferred: false,
      unconfirmed: [],
      linkedClaims: [{ id: "A-01", text: "Company A suspended the account." }],
    };
    render(
      <CaseDetails
        parties={[{ ...row, name: "Company A", role: null }]}
        timeline={[{ ...row, time: null, event: "Company A suspended the account." }]}
        impacts={[]}
        caseId="case-1"
        onSelectSource={vi.fn()}
        activeSourceKey={null}
      />,
    );
    expect(
      screen.getByText("No date or time extracted; check the linked claim"),
    ).toBeInTheDocument();
    expect(screen.getAllByText("Related findings")).toHaveLength(2);
    fireEvent.click(screen.getAllByText("Related findings")[0]);
    expect(screen.getAllByRole("link", { name: "View finding" })[0]).toHaveAttribute(
      "href",
      "/case/case-1/analysis/findings?finding=A-01",
    );
    expect(screen.queryByText(/earlier Judgement/)).not.toBeInTheDocument();
  });
});
