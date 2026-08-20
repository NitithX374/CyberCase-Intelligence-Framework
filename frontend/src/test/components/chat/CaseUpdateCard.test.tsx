import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CaseUpdateCard } from "@/components/conversation/CaseUpdateCard";
import type { CaseUpdateView } from "@/lib/case-update";

function updatedView(): CaseUpdateView {
  return {
    status: "updated",
    parentVersion: 3,
    childVersion: 4,
    added: [
      {
        targetType: "evidence",
        targetId: "E-010",
        summary: "E-010 · Authentication log",
      },
    ],
    changed: [
      {
        targetType: "relationship",
        targetId: "REL-004",
        field: "status",
        oldValue: "not_established",
        newValue: "suspected",
      },
    ],
    currentUnresolvedInformation: [
      {
        topic: "Credential source",
        description: "The credential source is not reported.",
        status: "NOT_PROVIDED",
        priority: "high",
      },
    ],
  };
}

describe("CaseUpdateCard", () => {
  it("renders exact versions, delta operations, and current unresolved items", () => {
    render(<CaseUpdateCard update={updatedView()} />);

    const card = screen.getByRole("region", { name: "Case State update" });
    expect(within(card).getByText("Case State V3 → V4")).toBeInTheDocument();
    expect(within(card).getByText("E-010 · Authentication log")).toBeInTheDocument();
    expect(within(card).getByText("REL-004 · status")).toBeInTheDocument();
    expect(within(card).getByText("not_established → suspected")).toBeInTheDocument();
    expect(within(card).getByText("Credential source")).toBeInTheDocument();
    expect(within(card).queryByText(/resolved gap/i)).not.toBeInTheDocument();
  });

  it("renders no-change without claiming a new version", () => {
    render(
      <CaseUpdateCard
        update={{
          ...updatedView(),
          status: "no_change",
          parentVersion: 2,
          childVersion: null,
          added: [],
          changed: [],
        }}
      />,
    );

    expect(screen.getByText("Case State unchanged")).toBeInTheDocument();
    expect(screen.getByText("Case State V2 · No new version")).toBeInTheDocument();
    expect(screen.getByText("No ADD operations.")).toBeInTheDocument();
    expect(screen.getByText("No MODIFY operations.")).toBeInTheDocument();
  });

  it("distinguishes missing validation from a completed empty gap list", () => {
    const { rerender } = render(
      <CaseUpdateCard
        update={{ ...updatedView(), currentUnresolvedInformation: null }}
      />,
    );
    expect(
      screen.getByText("No validated Gap Analysis is available."),
    ).toBeInTheDocument();

    rerender(
      <CaseUpdateCard
        update={{ ...updatedView(), currentUnresolvedInformation: [] }}
      />,
    );
    expect(screen.getByText("No unresolved items were returned.")).toBeInTheDocument();
  });
});
