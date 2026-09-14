import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkspaceSidebar } from "@/components/layout/WorkspaceSidebar";
import type { CaseRead } from "@/lib/api";

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    user: { id: "u1", name: "Test Analyst", email: "analyst@example.com" },
    isLoading: false,
    logout: vi.fn(),
    isLoggingOut: false,
  }),
}));

describe("WorkspaceSidebar", () => {
  const sampleCases: CaseRead[] = [
    {
      id: "thread-1",
      title: "คดีการบุกรุกเว็บเซิร์ฟเวอร์",
      status: "answered",
      chat_thread_id: "thread-1",
      evidence_revision: 1,
      processing_status: "idle",
      has_pending_clarification: false,
      analysis_freshness: "current",
      created_at: "2026-03-10T08:00:00Z",
      updated_at: "2026-03-10T08:10:00Z",
    },
  ];

  it("renders the compact CaseFleet-style workspace rail", () => {
    render(
      <WorkspaceSidebar
        cases={sampleCases}
        activeCaseId="thread-1"
        casesLoading={false}
        casesError={null}
        onSelectCase={vi.fn()}
        onNewCase={vi.fn()}
        onRequestDelete={vi.fn()}
        deletingCaseId={null}
        activeView="overview"
        onViewChange={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: /New case/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cases" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Case analysis" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Case materials" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Technical context" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Case report" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Chat$/i })).not.toBeInTheDocument();
    expect(screen.queryByText(/Investigation Issues/i)).not.toBeInTheDocument();
  });

  it("opens saved cases and routes through rail shortcuts", () => {
    const handleViewChange = vi.fn();

    render(
      <WorkspaceSidebar
        cases={sampleCases}
        activeCaseId="thread-1"
        casesLoading={false}
        casesError={null}
        onSelectCase={vi.fn()}
        onNewCase={vi.fn()}
        onRequestDelete={vi.fn()}
        deletingCaseId={null}
        activeView="overview"
        onViewChange={handleViewChange}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Cases" }));
    expect(screen.getByRole("region", { name: "Saved cases" })).toBeInTheDocument();
    expect(screen.getByText("คดีการบุกรุกเว็บเซิร์ฟเวอร์")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Case materials" }));
    expect(handleViewChange).toHaveBeenCalledWith("materials");
    expect(screen.queryByRole("region", { name: "Saved cases" })).not.toBeInTheDocument();
  });
});
