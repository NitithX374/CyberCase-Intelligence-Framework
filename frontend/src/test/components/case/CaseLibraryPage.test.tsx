import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { CaseRead } from "@/lib/api";
import { CaseLibraryPage } from "@/components/case-library/CaseLibraryPage";
import { useCaseMutations, useCases } from "@/hooks/useCaseQueries";

const routerPush = vi.fn();
const mutateAsync = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: routerPush }),
}));

vi.mock("@/hooks/useCaseQueries", () => ({
  useCaseMutations: vi.fn(),
  useCases: vi.fn(),
}));

function caseRecord(overrides: Partial<CaseRead> = {}): CaseRead {
  return {
    id: "case-1",
    user_id: "user-1",
    title: "Police Investigation Report",
    status: "answered",
    evidence_revision: 2,
    latest_analysis_result_id: "analysis-1",
    active_run_id: null,
    latest_run_id: "run-1",
    processing_status: "idle",
    has_pending_clarification: false,
    analysis_freshness: "current",
    created_at: "2026-09-10T10:00:00Z",
    updated_at: "2026-09-14T10:00:00Z",
    ...overrides,
  };
}

function configureQuery(cases: CaseRead[]) {
  vi.mocked(useCases).mockReturnValue({
    data: cases,
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  } as never);
  vi.mocked(useCaseMutations).mockReturnValue({
    createMutation: {
      isPending: false,
      error: null,
      mutateAsync,
    },
  } as never);
}

describe("CaseLibraryPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mutateAsync.mockResolvedValue(caseRecord({ id: "new-case", title: "New case", latest_analysis_result_id: null }));
    configureQuery([
      caseRecord(),
      caseRecord({ id: "case-2", title: "SpeedFood System Architecture", updated_at: "2026-09-12T10:00:00Z", latest_analysis_result_id: null, status: "idle", analysis_freshness: "missing" }),
    ]);
  });

  it("renders the latest case and the complete Case library", () => {
    render(<CaseLibraryPage />);

    expect(screen.getByRole("heading", { name: "All cases" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Continue where you left off" })).toBeInTheDocument();
    expect(screen.getAllByText("Police Investigation Report")).toHaveLength(2);
    expect(screen.getByText("SpeedFood System Architecture")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "New case" })).toBeInTheDocument();
  });

  it("filters cases by title and switches between grid and list views", () => {
    render(<CaseLibraryPage />);

    fireEvent.change(screen.getByPlaceholderText("Search cases"), { target: { value: "SpeedFood" } });

    expect(screen.getByText("SpeedFood System Architecture")).toBeInTheDocument();
    expect(screen.queryByText("Police Investigation Report")).not.toBeInTheDocument();

    const listButton = screen.getByRole("button", { name: "List view" });
    fireEvent.click(listButton);
    expect(listButton).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Grid view" })).toHaveAttribute("aria-pressed", "false");
  });

  it("creates a Case and routes to Intake when the new Case has no analysis", async () => {
    render(<CaseLibraryPage />);

    fireEvent.click(screen.getByRole("button", { name: "New case" }));

    await waitFor(() => expect(routerPush).toHaveBeenCalledWith("/case/new-case/intake"));
    expect(mutateAsync).toHaveBeenCalledTimes(1);
  });

  it("offers a first-case action when the library is empty", async () => {
    configureQuery([]);
    render(<CaseLibraryPage />);

    expect(screen.getByRole("heading", { name: "No saved cases yet" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Create your first case" }));

    await waitFor(() => expect(routerPush).toHaveBeenCalledWith("/case/new-case/intake"));
  });
});
