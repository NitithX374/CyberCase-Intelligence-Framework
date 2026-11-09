import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkspaceHeader } from "@/features/workspace/WorkspaceHeader";
import type { CaseRead } from "@/lib/api/types";
import type { WorkspaceView } from "@/lib/casePaths";

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
  source_revision: 3,
  analysis_freshness: "current",
  created_at: "2026-09-14T08:00:00Z",
  updated_at: "2026-09-14T08:10:00Z",
};

interface HeaderOptions {
  activeView?: WorkspaceView;
  status?: string;
  statusNeedsAttention?: boolean;
  analyzeLabel?: string;
  canAnalyze?: boolean;
  onAnalyze?: () => void;
  onViewChange?: (view: WorkspaceView) => void;
  onNewCase?: () => void;
  onRenameCase?: (title: string) => void;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
}

function renderHeader(options: HeaderOptions = {}) {
  return render(
    <WorkspaceHeader
      activeCase={sampleCase}
      activeView={options.activeView ?? "analysis"}
      creatingCase={false}
      status={options.status ?? "Analysis up to date"}
      statusNeedsAttention={options.statusNeedsAttention ?? false}
      analyzeLabel={options.analyzeLabel ?? "Analyze again"}
      canAnalyze={options.canAnalyze ?? true}
      onAnalyze={options.onAnalyze}
      onViewChange={options.onViewChange ?? vi.fn()}
      onNewCase={options.onNewCase ?? vi.fn()}
      onRenameCase={options.onRenameCase}
      isChatOpen={options.isChatOpen}
      onToggleChat={options.onToggleChat}
    />,
  );
}

const viewButtons = () =>
  within(screen.getByRole("navigation", { name: "Case workspace views" })).getAllByRole("button");

describe("WorkspaceHeader", () => {
  it("names the three views and marks the current one", () => {
    const onViewChange = vi.fn();
    renderHeader({ onViewChange, isChatOpen: false, onToggleChat: vi.fn() });

    expect(screen.getByRole("heading", { name: "Payment Review" })).toBeInTheDocument();
    const views = within(screen.getByRole("navigation", { name: "Case workspace views" }));
    expect(viewButtons().map((item) => item.textContent)).toEqual(["Reading", "Sources", "Report"]);
    expect(views.getByRole("button", { name: "Reading" })).toHaveAttribute("aria-current", "page");
    expect(views.getByRole("button", { name: "Sources" })).not.toHaveAttribute("aria-current");
    expect(views.queryByRole("button", { name: "Legal" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open Ask" })).toBeInTheDocument();

    fireEvent.click(views.getByRole("button", { name: "Sources" }));
    expect(onViewChange).toHaveBeenCalledWith("sources");
    fireEvent.click(views.getByRole("button", { name: "Report" }));
    expect(onViewChange).toHaveBeenCalledWith("report");
    fireEvent.click(views.getByRole("button", { name: "Reading" }));
    expect(onViewChange).toHaveBeenCalledWith("analysis");
  });

  it("counts the legal route as the Reading view", () => {
    renderHeader({ activeView: "legal" });

    const current = viewButtons().filter((item) => item.getAttribute("aria-current") === "page");
    expect(current.map((item) => item.textContent)).toEqual(["Reading"]);
  });

  it("shows the case's counts and how many findings to check", () => {
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        status="Analysis up to date"
        statusNeedsAttention={false}
        analyzeLabel="Analyze again"
        canAnalyze
        findingCount={5}
        flaggedCount={2}
        sourceCount={1}
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
      />,
    );

    expect(screen.getByText("1 source")).toBeInTheDocument();
    expect(screen.getByText("2/5")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Create report" })).toHaveAttribute(
      "href",
      "/case/case-1/report",
    );
  });

  it.each(["sources", "report"] as const)(
    "shows a slim title bar on the %s view, without chips, ring or Create report",
    (activeView) => {
      const onAnalyze = vi.fn();
      render(
        <WorkspaceHeader
          activeCase={sampleCase}
          activeView={activeView}
          creatingCase={false}
          status="Out of date: sources changed"
          statusNeedsAttention
          analyzeLabel="Analyze"
          canAnalyze
          findingCount={5}
          flaggedCount={2}
          sourceCount={1}
          analysedAt="2026-09-14T08:10:00Z"
          onAnalyze={onAnalyze}
          onViewChange={vi.fn()}
          onNewCase={vi.fn()}
          onRenameCase={vi.fn()}
        />,
      );

      expect(screen.getByRole("heading", { level: 1, name: "Payment Review" })).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Rename case" })).toBeInTheDocument();
      expect(screen.getByRole("status")).toHaveTextContent("Out of date: sources changed");
      const analyze = screen.getByRole("button", { name: "Analyze" });
      expect(analyze).toHaveClass("btn-primary");
      fireEvent.click(analyze);
      expect(onAnalyze).toHaveBeenCalledOnce();
      expect(screen.queryByText("1 source")).not.toBeInTheDocument();
      expect(screen.queryByText(/^Analyzed/)).not.toBeInTheDocument();
      expect(screen.queryByText("2/5")).not.toBeInTheDocument();
      expect(screen.queryByRole("link", { name: "Create report" })).not.toBeInTheDocument();
    },
  );

  it("shows when the case was analyzed on the band", () => {
    render(
      <WorkspaceHeader
        activeCase={sampleCase}
        activeView="analysis"
        creatingCase={false}
        status="Analysis up to date"
        statusNeedsAttention={false}
        analyzeLabel="Analyze again"
        canAnalyze
        analysedAt="2026-09-14T08:10:00Z"
        onViewChange={vi.fn()}
        onNewCase={vi.fn()}
      />,
    );

    expect(screen.getByText(/^Analyzed /)).toBeInTheDocument();
  });

  it("lets the keyboard reach every view, not only the current one", () => {
    renderHeader();
    const views = within(screen.getByRole("navigation", { name: "Case workspace views" }));

    expect(views.queryByRole("tablist")).not.toBeInTheDocument();
    expect(viewButtons()).toHaveLength(3);
    for (const item of viewButtons()) {
      expect(item.tabIndex).toBe(0);
    }
  });

  it("says where the analysis stands beside the views, never on a tab", () => {
    renderHeader({
      activeView: "sources",
      status: "Out of date: sources changed",
      statusNeedsAttention: true,
    });

    expect(screen.getByRole("status")).toHaveTextContent("Out of date: sources changed");
    expect(viewButtons().map((item) => item.textContent)).toEqual(["Reading", "Sources", "Report"]);
  });

  it("offers one Analyze button that runs the analysis", () => {
    const onAnalyze = vi.fn();
    renderHeader({ analyzeLabel: "Analyze", onAnalyze });

    const buttons = screen.getAllByRole("button", { name: /Analy/ });
    expect(buttons).toHaveLength(1);
    expect(buttons[0]).toHaveTextContent("Analyze");
    expect(buttons[0]).toBeEnabled();
    fireEvent.click(buttons[0]);
    expect(onAnalyze).toHaveBeenCalledOnce();
  });

  it("holds the Analyze button while an analysis cannot start", () => {
    const onAnalyze = vi.fn();
    renderHeader({
      status: "Analyzing…",
      analyzeLabel: "Analyzing…",
      canAnalyze: false,
      onAnalyze,
    });

    expect(screen.getByRole("status")).toHaveTextContent("Analyzing…");
    const button = screen.getByRole("button", { name: "Analyzing…" });
    expect(button).toBeDisabled();
    fireEvent.click(button);
    expect(onAnalyze).not.toHaveBeenCalled();
  });

  it("shows no Analyze button when there is nothing to analyse", () => {
    renderHeader();

    expect(screen.queryByRole("button", { name: /Analy/ })).not.toBeInTheDocument();
  });

  it("keeps the case library and a new case behind the account menu", () => {
    const onNewCase = vi.fn();
    renderHeader({ onNewCase });

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
  it("offers a rename button named for screen readers and on hover", () => {
    renderHeader({ onRenameCase: vi.fn() });

    expect(screen.getByRole("button", { name: "Rename case" })).toHaveAttribute(
      "title",
      "Rename case",
    );
  });

  it("opens a field on the title, already selected", () => {
    renderHeader({ onRenameCase: vi.fn() });

    fireEvent.click(screen.getByRole("button", { name: "Rename case" }));

    const field = screen.getByLabelText("Case title");
    expect(field).toHaveValue("Payment Review");
    expect(field).toHaveFocus();
  });

  it("keeps what was typed when the field is submitted", () => {
    const onRenameCase = vi.fn();
    renderHeader({ onRenameCase });
    fireEvent.click(screen.getByRole("button", { name: "Rename case" }));

    const field = screen.getByLabelText("Case title");
    fireEvent.change(field, { target: { value: "  Ransomware at the clinic  " } });
    fireEvent.submit(field);

    expect(onRenameCase).toHaveBeenCalledWith("Ransomware at the clinic");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Payment Review");
  });

  it("abandons the change on Escape", () => {
    const onRenameCase = vi.fn();
    renderHeader({ onRenameCase });
    fireEvent.click(screen.getByRole("button", { name: "Rename case" }));

    const field = screen.getByLabelText("Case title");
    fireEvent.change(field, { target: { value: "Something else" } });
    fireEvent.keyDown(field, { key: "Escape" });

    expect(onRenameCase).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Rename case" })).toBeInTheDocument();
  });

  it("does not ask the server for a title that did not change", () => {
    const onRenameCase = vi.fn();
    renderHeader({ onRenameCase });
    fireEvent.click(screen.getByRole("button", { name: "Rename case" }));

    fireEvent.submit(screen.getByLabelText("Case title"));

    expect(onRenameCase).not.toHaveBeenCalled();
  });

  it("offers no rename button when the workspace cannot rename", () => {
    renderHeader();

    expect(screen.queryByRole("button", { name: "Rename case" })).not.toBeInTheDocument();
  });
});
