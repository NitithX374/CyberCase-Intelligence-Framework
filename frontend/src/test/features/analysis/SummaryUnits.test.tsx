import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SummaryUnits } from "@/features/analysis/SummaryUnits";
import type { SummaryUnit } from "@/features/analysis/types";

const caseId = "22222222-2222-4222-8222-222222222222";

const units: SummaryUnit[] = [
  { text: "A share was encrypted", claimIds: ["A-01"], supportNote: null },
  {
    text: "Both demands were made",
    claimIds: ["A-03", "A-07"],
    supportNote: "Some cited quotations were not found in the sources.",
  },
  { text: "Someone is to blame", claimIds: [], supportNote: "Not linked to any claim." },
];

describe("Summary units", () => {
  it("ends each unit with the claims it rests on, each a plain link to that finding", () => {
    render(<SummaryUnits caseId={caseId} units={units} />);

    const [first, second] = screen.getAllByText(/A share was encrypted|Both demands were made/, {
      selector: "p",
    });
    expect(first).toHaveTextContent("A share was encrypted [A-01]");
    expect(within(first).getByRole("link", { name: "A-01" })).toHaveAttribute(
      "href",
      `/case/${caseId}/analysis/findings?finding=A-01`,
    );
    expect(second).toHaveTextContent("Both demands were made [A-03, A-07]");
    expect(
      within(second)
        .getAllByRole("link")
        .map((link) => link.getAttribute("href")),
    ).toEqual([
      `/case/${caseId}/analysis/findings?finding=A-03`,
      `/case/${caseId}/analysis/findings?finding=A-07`,
    ]);
  });

  it("puts one plain line under a unit that is not wholly supported, and none under one that is", () => {
    render(<SummaryUnits caseId={caseId} units={units} />);

    const [first, second, third] = screen.getAllByRole("paragraph");
    expect(first).toHaveTextContent(/^A share was encrypted \[A-01\]$/);
    expect(second).toHaveTextContent(
      "Both demands were made [A-03, A-07]Some cited quotations were not found in the sources.",
    );
    expect(third).toHaveTextContent("Someone is to blame" + "Not linked to any claim.");
    expect(within(third).queryByRole("link")).not.toBeInTheDocument();
    expect(third).not.toHaveTextContent("[");
  });

  it("draws no badge, pill or icon", () => {
    const { container } = render(<SummaryUnits caseId={caseId} units={units} />);

    expect(container.querySelector("svg, img, button")).toBeNull();
    expect(container.innerHTML).not.toMatch(/rounded|bg-/);
  });
});
