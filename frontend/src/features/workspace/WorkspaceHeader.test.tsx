import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkspaceHeader } from "./WorkspaceHeader";
import type { CaseRead } from "@/lib/api";

vi.mock("@/features/auth/useAuth", () => ({
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
  source_revision: 3,
  analysis_freshness: "current",
  created_at: "2026-09-14T08:00:00Z",
  updated_at: "2026-09-14T08:10:00Z",
};

function analysisDot() {
  return screen.getByRole("tab", { name: "Analysis" }).querySelector('[aria-hidden="true"]');
}

describe("WorkspaceHeader", () => {
  it("keeps every route meaning, and leaves Analyze to the pages", () => {
    const onViewChange = vi.fn();

    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        isAnalyzing={false}
        isStale={false}
        onViewChange={onViewChange}
        onNewCase={vi.fn()}
        isChatOpen={false}
        onToggleChat={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "Payment Review" })).toBeInTheDocument();
    expect(screen.getAllByRole("tab")).toHaveLength(3);
    expect(screen.getByRole("tab", { name: "Analysis" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("button", { name: "Open Ask" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: "Sources" }));
    expect(onViewChange).toHaveBeenCalledWith("sources");
    fireEvent.click(screen.getByRole("tab", { name: "Legal" }));
    expect(onViewChange).toHaveBeenCalledWith("legal");

    expect(screen.queryByRole("button", { name: /Analyze/ })).not.toBeInTheDocument();
    expect(analysisDot()).toBeNull();
  });

  it("marks the Analysis tab when the analysis is behind the sources", () => {
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="sources"
        creatingCase={false}
        isAnalyzing={false}
        isStale
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
      />,
    );
    expect(analysisDot()).toHaveClass("bg-unresolved");
  });

  it("marks the Analysis tab while an analysis runs, without renaming it", () => {
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="sources"
        creatingCase={false}
        isAnalyzing
        isStale
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
      />,
    );
    expect(analysisDot()).toHaveClass("bg-accent");
  });

  it("keeps the case library and a new case behind the account menu", () => {
    const onNewCase = vi.fn();
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        isAnalyzing={false}
        isStale={false}
        onViewChange={vi.fn()}
        onNewCase={onNewCase}
      />,
    );

    expect(screen.queryByRole("button", { name: "New case" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Open account menu" }));
    const libraryLinks = screen.getAllByRole("link", { name: "All cases" });
    expect(libraryLinks).toHaveLength(2);
    libraryLinks.forEach((link) => expect(link).toHaveAttribute("href", "/case"));
    fireEvent.click(screen.getByRole("button", { name: "New case" }));
    expect(onNewCase).toHaveBeenCalledOnce();
  });
});

describe("renaming a case from the header", () => {
  const renderHeader = (onRenameCase: (title: string) => void) =>
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        isAnalyzing={false}
        isStale={false}
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
        onRenameCase={onRenameCase}
      />,
    );

  it("opens a field on the title, already selected", () => {
    renderHeader(vi.fn());

    fireEvent.click(screen.getByRole("button", { name: "Rename case" }));

    const field = screen.getByLabelText("Case title");
    expect(field).toHaveValue("Payment Review");
    expect(field).toHaveFocus();
  });

  it("keeps what was typed when the field is submitted", () => {
    const onRenameCase = vi.fn();
    renderHeader(onRenameCase);
    fireEvent.click(screen.getByRole("button", { name: "Rename case" }));

    const field = screen.getByLabelText("Case title");
    fireEvent.change(field, { target: { value: "  Ransomware at the clinic  " } });
    fireEvent.submit(field);

    expect(onRenameCase).toHaveBeenCalledWith("Ransomware at the clinic");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Payment Review");
  });

  it("abandons the change on Escape", () => {
    const onRenameCase = vi.fn();
    renderHeader(onRenameCase);
    fireEvent.click(screen.getByRole("button", { name: "Rename case" }));

    const field = screen.getByLabelText("Case title");
    fireEvent.change(field, { target: { value: "Something else" } });
    fireEvent.keyDown(field, { key: "Escape" });

    expect(onRenameCase).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Rename case" })).toBeInTheDocument();
  });

  it("does not ask the server for a title that did not change", () => {
    const onRenameCase = vi.fn();
    renderHeader(onRenameCase);
    fireEvent.click(screen.getByRole("button", { name: "Rename case" }));

    fireEvent.submit(screen.getByLabelText("Case title"));

    expect(onRenameCase).not.toHaveBeenCalled();
  });

  it("offers no pencil when the workspace cannot rename", () => {
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        isAnalyzing={false}
        isStale={false}
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
      />,
    );

    expect(screen.queryByRole("button", { name: "Rename case" })).not.toBeInTheDocument();
  });
});
