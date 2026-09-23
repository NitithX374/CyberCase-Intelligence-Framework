import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { CaseRead } from "@/lib/api";
import { CaseLibraryPage } from "@/components/case-library/CaseLibraryPage";
import { useCaseMutations, useCases } from "@/hooks/useCaseQueries";

const routerPush = vi.fn();
const mutateAsync = vi.fn();
const deleteCase = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: routerPush }),
}));

vi.mock("@/hooks/useCaseQueries", () => ({
  useCaseMutations: vi.fn(),
  useCases: vi.fn(),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({
    user: { id: "u1", name: "Test Analyst", email: "analyst@example.com" },
    isLoading: false,
    logout: vi.fn(),
    isLoggingOut: false,
  }),
}));

function caseRecord(overrides: Partial<CaseRead> = {}): CaseRead {
  return {
    id: "case-1",
    user_id: "user-1",
    title: "Police Investigation Report",
    status: "answered",
    source_revision: 2,
    latest_analysis_result_id: "analysis-1",
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
    deleteMutation: {
      isPending: false,
      error: null,
      variables: undefined,
      mutateAsync: deleteCase,
    },
  } as never);
}

describe("CaseLibraryPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mutateAsync.mockResolvedValue(
      caseRecord({ id: "new-case", title: "New case", latest_analysis_result_id: null }),
    );
    configureQuery([
      caseRecord(),
      caseRecord({
        id: "case-2",
        title: "SpeedFood System Architecture",
        updated_at: "2026-09-12T10:00:00Z",
        latest_analysis_result_id: null,
        status: "idle",
        analysis_freshness: "missing",
      }),
    ]);
  });

  it("renders every case once, most recent first", () => {
    render(<CaseLibraryPage />);

    expect(screen.getByRole("heading", { name: "All cases" })).toBeInTheDocument();
    const titles = screen
      .getAllByRole("link")
      .map((link) => link.textContent ?? "")
      .filter((text) => /Police|SpeedFood/.test(text));
    expect(titles).toHaveLength(2);
    expect(titles[0]).toContain("Police Investigation Report");
    expect(titles[1]).toContain("SpeedFood System Architecture");
    expect(screen.getByText("Analyzed")).toBeInTheDocument();
    expect(screen.getByText("Not analyzed")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "New case" })).toBeInTheDocument();
  });

  it("filters cases by title and switches between grid and list views", () => {
    render(<CaseLibraryPage />);

    fireEvent.change(screen.getByPlaceholderText("Search cases"), {
      target: { value: "SpeedFood" },
    });

    expect(screen.getByText("SpeedFood System Architecture")).toBeInTheDocument();
    expect(screen.queryByText("Police Investigation Report")).not.toBeInTheDocument();

    const listButton = screen.getByRole("button", { name: "List view" });
    const gridButton = screen.getByRole("button", { name: "Grid view" });
    expect(listButton).toHaveAttribute("aria-pressed", "true");
    fireEvent.click(gridButton);
    expect(gridButton).toHaveAttribute("aria-pressed", "true");
    expect(listButton).toHaveAttribute("aria-pressed", "false");
  });

  it("creates a Case and routes to its sources when the new Case has no analysis", async () => {
    render(<CaseLibraryPage />);

    fireEvent.click(screen.getByRole("button", { name: "New case" }));

    await waitFor(() => expect(routerPush).toHaveBeenCalledWith("/case/new-case/sources"));
    expect(mutateAsync).toHaveBeenCalledTimes(1);
  });

  it("offers a first-case action when the library is empty", async () => {
    configureQuery([]);
    render(<CaseLibraryPage />);

    expect(screen.getByRole("heading", { name: "No saved cases yet" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Create your first case" }));

    await waitFor(() => expect(routerPush).toHaveBeenCalledWith("/case/new-case/sources"));
  });

  it("deletes a case from the library, which is the only place it can be", async () => {
    render(<CaseLibraryPage />);
    fireEvent.click(screen.getByRole("button", { name: "Delete Police Investigation Report" }));
    expect(screen.getByRole("heading", { name: "Delete this case?" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Delete case" }));
    await waitFor(() => expect(deleteCase).toHaveBeenCalledWith("case-1"));
  });
});
