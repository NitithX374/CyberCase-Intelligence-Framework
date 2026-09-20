import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import type { CaseRead } from "@/lib/api";

vi.mock("@/hooks/useAuth", () => ({
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

describe("WorkspaceHeader", () => {
  it("keeps both route meanings and runs the analysis from here", () => {
    const onViewChange = vi.fn();
    const onAnalyze = vi.fn();

    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        hasAnalysis
        canAnalyze
        isAnalyzing={false}
        isStale={false}
        onAnalyze={onAnalyze}
        onViewChange={onViewChange}
        onNewCase={vi.fn()}
        isChatOpen={false}
        onToggleChat={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "Payment Review" })).toBeInTheDocument();
    expect(screen.getAllByRole("tab")).toHaveLength(2);
    expect(screen.getByRole("tab", { name: "Analysis" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("button", { name: "Open Ask" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("tab", { name: "Sources" }));
    expect(onViewChange).toHaveBeenCalledWith("sources");

    // The analysis moved here from the sources rail, so every view can start it.
    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    expect(onAnalyze).toHaveBeenCalledOnce();
  });

  it("will not analyse a case with nothing to analyse", () => {
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        hasAnalysis={false}
        canAnalyze={false}
        isAnalyzing={false}
        isStale={false}
        onAnalyze={vi.fn()}
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Analyze" })).toBeDisabled();
  });

  it("says so when the analysis is behind the material", () => {
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        hasAnalysis
        canAnalyze
        isAnalyzing={false}
        isStale
        onAnalyze={vi.fn()}
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
      />,
    );
    expect(screen.getByRole("button", { name: "Analyze latest" })).toBeInTheDocument();
  });

  it("shows the running state while follow-up analysis is in flight", () => {
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        hasAnalysis
        canAnalyze
        isAnalyzing
        isStale
        onAnalyze={vi.fn()}
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: "Analyzing…" })).toBeDisabled();
    expect(screen.getAllByText("Analysing")).toHaveLength(2);
  });
});

describe("renaming a case from the header", () => {
  const renderHeader = (onRenameCase: (title: string) => void) =>
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        hasAnalysis
        canAnalyze
        isAnalyzing={false}
        isStale={false}
        onAnalyze={vi.fn()}
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
        hasAnalysis
        canAnalyze
        isAnalyzing={false}
        isStale={false}
        onAnalyze={vi.fn()}
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
      />,
    );

    expect(screen.queryByRole("button", { name: "Rename case" })).not.toBeInTheDocument();
  });
});
