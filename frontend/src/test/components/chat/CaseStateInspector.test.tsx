import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CaseStateInspector } from "@/components/conversation/CaseStateInspector";
import type { CaseUpdateView } from "@/lib/case-update";

function sampleUpdate(parentVersion = 1, childVersion = 2): CaseUpdateView {
  return {
    status: "updated",
    parentVersion,
    childVersion,
    added: [
      {
        targetType: "missing_information",
        targetId: "MISS-001",
        summary: "MISS-001 · Incident timestamp missing",
      },
    ],
    changed: [],
    currentUnresolvedInformation: [
      {
        topic: "Incident timestamp",
        description: "Exact timestamp is unknown",
        status: "NOT_PROVIDED",
        priority: "high",
        reason: "Without timestamp, correlation with firewall logs is impossible.",
        affects: "Attacker timeline is not established.",
      },
    ],
  };
}

describe("CaseStateInspector", () => {
  it("renders empty state when there are no updates", () => {
    render(
      <CaseStateInspector
        updates={[]}
        selectedOrdinal={null}
        onSelectOrdinal={vi.fn()}
        isOpen={true}
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByText("No Case State Updates Yet")).toBeInTheDocument();
  });

  it("renders the selected update card and version info", () => {
    render(
      <CaseStateInspector
        updates={[{ ordinal: 2, update: sampleUpdate(1, 2) }]}
        selectedOrdinal={2}
        onSelectOrdinal={vi.fn()}
        isOpen={true}
        onClose={vi.fn()}
      />,
    );

    const inspector = screen.getByRole("complementary", {
      name: "Case State Inspector",
    });
    expect(within(inspector).getByText("Case State V1 → V2")).toBeInTheDocument();
    expect(
      within(inspector).getByText("MISS-001 · Incident timestamp missing"),
    ).toBeInTheDocument();
  });

  it("switches updates using history tabs", () => {
    const handleSelectOrdinal = vi.fn();
    render(
      <CaseStateInspector
        updates={[
          { ordinal: 2, update: sampleUpdate(1, 2) },
          { ordinal: 4, update: sampleUpdate(2, 3) },
        ]}
        selectedOrdinal={2}
        onSelectOrdinal={handleSelectOrdinal}
        isOpen={true}
        onClose={vi.fn()}
      />,
    );

    const historyTab = screen.getByRole("button", { name: /#4 V2 → V3/i });
    fireEvent.click(historyTab);

    expect(handleSelectOrdinal).toHaveBeenCalledWith(4);
  });

  it("calls onClose when close button is clicked", () => {
    const handleClose = vi.fn();
    render(
      <CaseStateInspector
        updates={[{ ordinal: 2, update: sampleUpdate(1, 2) }]}
        selectedOrdinal={2}
        onSelectOrdinal={vi.fn()}
        isOpen={true}
        onClose={handleClose}
      />,
    );

    const closeBtn = screen.getByRole("button", {
      name: "Close Case State Inspector",
    });
    fireEvent.click(closeBtn);

    expect(handleClose).toHaveBeenCalledOnce();
  });

  it("switches to the dedicated Current Unresolved page/tab and expands gap details", () => {
    render(
      <CaseStateInspector
        updates={[{ ordinal: 2, update: sampleUpdate(1, 2) }]}
        selectedOrdinal={2}
        onSelectOrdinal={vi.fn()}
        isOpen={true}
        onClose={vi.fn()}
      />,
    );

    const unresolvedTab = screen.getByRole("button", {
      name: /Unresolved/i,
    });
    fireEvent.click(unresolvedTab);

    expect(screen.getByText("Incident timestamp")).toBeInTheDocument();
    expect(screen.getByText("Exact timestamp is unknown")).toBeInTheDocument();
    expect(screen.getAllByText(/high/i)[0]).toBeInTheDocument();

    const summary = screen.getByText("Incident timestamp");
    const details = summary.closest("details");
    expect(details).not.toHaveAttribute("open");

    fireEvent.click(summary);

    expect(details).toHaveAttribute("open");
    expect(screen.getByText("Why it matters")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Without timestamp, correlation with firewall logs is impossible.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText("Affected conclusion")).toBeInTheDocument();
    expect(
      screen.getByText("Attacker timeline is not established."),
    ).toBeInTheDocument();
  });

  it("switches to the dedicated MITRE Candidates tab and renders candidates", () => {
    render(
      <CaseStateInspector
        updates={[
          {
            ordinal: 2,
            update: sampleUpdate(1, 2),
            mitreCandidates: [
              {
                associationId: "MA-01",
                techniqueId: "T1059.001",
                techniqueName: "PowerShell",
                claims: [
                  {
                    claimId: "A-01",
                    text: "PowerShell executed with bypass flags.",
                    claimType: "reported",
                    epistemicStatus: "reported",
                  },
                ],
                reason: "Activity indicates execution of PowerShell scripts.",
              },
            ],
          },
        ]}
        selectedOrdinal={2}
        onSelectOrdinal={vi.fn()}
        isOpen={true}
        onClose={vi.fn()}
      />,
    );

    const mitreTab = screen.getByRole("button", {
      name: /MITRE/i,
    });
    fireEvent.click(mitreTab);

    expect(screen.getByText("T1059.001 — PowerShell")).toBeInTheDocument();
    expect(screen.getByText("A-01")).toBeInTheDocument();
    expect(
      screen.getByText("PowerShell executed with bypass flags."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Activity indicates execution of PowerShell scripts."),
    ).toBeInTheDocument();
    expect(screen.getByText("Candidate only")).toBeInTheDocument();
  });
});
