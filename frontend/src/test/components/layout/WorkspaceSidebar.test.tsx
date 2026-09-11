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
      created_at: "2026-03-10T08:00:00Z",
      updated_at: "2026-03-10T08:10:00Z",
    },
  ];

  it("renders the 5 case workspace tabs and does not include deleted Investigation Issues or chat tab", () => {
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

    // Section title
    expect(screen.getByText("Case")).toBeInTheDocument();

    // 5 Tabs
    expect(screen.getByRole("tab", { name: /Intake/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Overview/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Case Materials/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Technical Context/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Report/i })).toBeInTheDocument();

    // Chat is docked in Copilot, not in the sidebar tabs
    expect(screen.queryByRole("tab", { name: /^Chat$/i })).not.toBeInTheDocument();

    // Investigation Issues is deleted
    expect(screen.queryByRole("tab", { name: /Investigation Issues/i })).not.toBeInTheDocument();

    // New case button exists
    expect(screen.getByRole("button", { name: /New case/i })).toBeInTheDocument();
  });

  it("triggers onViewChange when a tab is clicked", () => {
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

    const materialsTab = screen.getByRole("tab", { name: /Case Materials/i });
    fireEvent.click(materialsTab);
    expect(handleViewChange).toHaveBeenCalledWith("materials");
  });
});
