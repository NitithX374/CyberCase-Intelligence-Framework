import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProjectionReview } from "@/features/analysis/ProjectionReview";
import { projectionReason } from "@/features/analysis/projectionChecks";
import { caseId } from "@/test/fixtures";
import type { ClaimBacked } from "@/features/analysis/types";

const row: ClaimBacked = {
  sources: [],
  inferred: false,
  unconfirmed: [],
  linkedClaims: [{ id: "A-01", text: "John sent an email." }],
  projectionGrounding: { verdict: "not_supported", reason: "neutral", model: "pinned-verifier" },
};

describe("description check details", () => {
  it("explains a withheld role and links to the exact supporting claim", () => {
    render(<ProjectionReview row={row} caseId={caseId} />);
    expect(
      screen.getByText(/Not supported by linked claims · Withheld from earlier Judgement/),
    ).toBeInTheDocument();
    expect(screen.getByText(/do not establish the complete description/)).toBeInTheDocument();
    expect(screen.getByText(/Its linked claims were still supplied/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "A-01" })).toHaveAttribute(
      "href",
      `/case/${caseId}/analysis/findings?finding=A-01`,
    );
    expect(screen.getByText(/John sent an email/)).toBeInTheDocument();
  });

  it("keeps verifier failure distinct from semantic rejection", () => {
    render(
      <ProjectionReview
        row={{
          ...row,
          projectionGrounding: {
            verdict: "unassessed",
            reason: "model_unavailable:weights_missing",
          },
        }}
      />,
    );
    expect(screen.getByText("Not assessed · Withheld from earlier Judgement")).toBeInTheDocument();
    expect(screen.getByText(/model files are missing/)).toBeInTheDocument();
  });

  it("makes no admission claim for a historical item without a check", () => {
    render(<ProjectionReview row={{ ...row, projectionGrounding: null }} />);
    expect(screen.getByText("Check not recorded · Judgement use not recorded")).toBeInTheDocument();
  });

  it("preserves an unknown backend reason instead of inventing an explanation", () => {
    expect(projectionReason({ verdict: "unassessed", reason: "new_reason" })).toBe(
      "Recorded check reason: new_reason",
    );
    expect(projectionReason({ verdict: "unassessed", reason: "context_limit" }, true)).toContain(
      "ยาวเกิน",
    );
  });
});
