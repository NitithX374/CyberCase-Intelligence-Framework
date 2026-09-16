import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import type { CaseRead } from "@/lib/api";

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    user: { id: "u1", name: "Test Analyst", email: "analyst@example.com" },
    isLoading: false,
    logout: vi.fn(),
    isLoggingOut: false,
  }),
}));

const sampleCase: CaseRead = {
  id: "case-1",
  title: "Payment Review",
  status: "answered",
  evidence_revision: 3,
  processing_status: "idle",
  has_pending_followup: false,
  analysis_freshness: "current",
  created_at: "2026-09-14T08:00:00Z",
  updated_at: "2026-09-14T08:10:00Z",
};

describe("WorkspaceHeader", () => {
  it("keeps the current five route meanings in the case header", () => {
    const onViewChange = vi.fn();

    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeCaseId={sampleCase.id}
        activeView="overview"
        cases={[sampleCase]}
        creatingCase={false}
        deletingCaseId={null}
        phase="ready"
        onViewChange={onViewChange}
        onSelectCase={vi.fn()}
        onNewCase={vi.fn()}
        onRequestDelete={vi.fn()}
        isChatOpen={false}
        onToggleChat={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "Payment Review" })).toBeInTheDocument();
    expect(screen.getAllByRole("tab")).toHaveLength(5);
    expect(screen.getByRole("tab", { name: "Overview" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("button", { name: "Open Ask" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: "Report" }));
    expect(onViewChange).toHaveBeenCalledWith("report");
  });
});
