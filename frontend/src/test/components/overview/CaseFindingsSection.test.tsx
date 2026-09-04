import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CaseFindingsSection } from "@/components/overview/CaseFindingsSection";
import type { CaseFinding, ClaimType, EpistemicStatus } from "@/lib/case-overview-contracts";
import { groupCaseFindings } from "@/lib/case-overview";

function finding(id: string, claimType: ClaimType = "reported", epistemicStatus: EpistemicStatus = "reported"): CaseFinding {
  return { id, text: `Original finding ${id}`, claimType, epistemicStatus,
    reasoningSummary: null, supportingSources: [], contradictingSources: [], mitreTechniques: [] };
}

describe("Grouped case findings", () => {
  it("preserves all combinations of claim type and status without inventing certainty", () => {
    const types: ClaimType[] = ["reported", "analytical_inference", "unknown"];
    const statuses: EpistemicStatus[] = ["reported", "suspected", "contradicted", "not_established", "unknown", "not_confirmed"];
    const findings = types.flatMap((type) => statuses.map((status) => finding(`${type}-${status}`, type, status)));
    const snapshot = structuredClone(findings);
    const groups = groupCaseFindings(findings);
    expect(groups.flatMap((group) => group.findings).sort((a, b) => a.id.localeCompare(b.id)))
      .toEqual([...findings].sort((a, b) => a.id.localeCompare(b.id)));
    expect(new Set(groups.flatMap((group) => group.findings.map((item) => item.id))).size).toBe(18);
    expect(groups.find((group) => group.id === "not_established")?.findings).toHaveLength(3);
    expect(groups.find((group) => group.id === "reported")?.findings).toEqual([findings[0]]);
    expect(findings).toEqual(snapshot);
  });

  it("keeps uncertainty visible before long reported groups and exposes every remaining finding", () => {
    const reported = Array.from({ length: 12 }, (_, index) => finding(`reported-${index}`));
    const uncertain = Array.from({ length: 7 }, (_, index) => finding(`uncertain-${index}`, "analytical_inference", "not_established"));
    const { container } = render(<CaseFindingsSection findings={[...reported, ...uncertain]} />);
    expect(container.querySelector("article")).toHaveTextContent("Original finding uncertain-0");
    const uncertainty = screen.getByRole("region", { name: "Not established 7" });
    expect(within(uncertainty).getAllByRole("article")).toHaveLength(7);
    expect(within(uncertainty).queryByRole("button", { name: /Show/ })).not.toBeInTheDocument();
    expect(screen.queryByText("Original finding reported-11")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Show all 12 reported information" }));
    expect(screen.getByText("Original finding reported-11")).toBeVisible();
    expect(screen.getAllByRole("article")).toHaveLength(19);
    fireEvent.click(screen.getByRole("button", { name: "Show fewer reported information" }));
    expect(screen.getAllByRole("article")).toHaveLength(12);
  });

  it("shows both axes for an inference without established support", () => {
    render(<CaseFindingsSection findings={[finding("inference", "analytical_inference", "not_established"), finding("missing", "unknown", "unknown")]} />);
    const inference = screen.getByRole("region", { name: "Not established 1" });
    expect(within(inference).getByRole("article")).toHaveTextContent("Analytical inference· Not established");
    expect(screen.getByRole("region", { name: "Unknown 1" })).toHaveTextContent("Original finding missing");
    expect(screen.queryByText(/Confirmed fact|Supported fact|False/)).not.toBeInTheDocument();
  });
});
