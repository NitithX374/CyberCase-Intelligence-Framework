import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useWorkspaceActivity } from "@/features/workspace/WorkspaceActivityContext";
import { httpError, refusal } from "@/test/httpErrors";
import CaseShellLayout from "./layout";

const caseId = "22222222-2222-4222-8222-222222222222";

const state = vi.hoisted(() => ({
  createCase: vi.fn(),
  startAnalysis: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => `/case/${caseId}/sources`,
  useParams: () => ({ caseId }),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));
vi.mock("@/features/cases/queries", () => ({
  useCases: () => ({ data: [] }),
  useCase: () => ({ data: undefined }),
  useCaseMutations: () => ({
    createMutation: { isPending: false, mutateAsync: state.createCase },
    deleteMutation: { isPending: false, mutateAsync: vi.fn() },
    updateMutation: { isPending: false, mutateAsync: vi.fn() },
  }),
}));
vi.mock("@/features/sources/queries", () => ({ useCaseSources: () => ({ data: [] }) }));
vi.mock("@/features/analysis/queries", () => ({
  useIsCaseAnalysisRunning: () => false,
  useStartCaseAnalysis: () => ({ mutateAsync: state.startAnalysis }),
}));
vi.mock("@/features/workspace/WorkspaceHeader", () => ({
  WorkspaceHeader: ({ onNewCase }: { onNewCase: () => void }) => (
    <button type="button" onClick={onNewCase}>
      New case
    </button>
  ),
}));
vi.mock("@/features/chat/WorkspaceChatPanel", () => ({ WorkspaceChatPanel: () => null }));

function AnalyzeButton() {
  const { runAnalysis } = useWorkspaceActivity();
  return (
    <button type="button" onClick={runAnalysis}>
      Analyze
    </button>
  );
}

beforeEach(() => {
  state.createCase.mockReset();
  state.startAnalysis.mockReset();
  localStorage.clear();
});

describe("CaseShellLayout", () => {
  it("tells the reader when a new case could not be created, and remembers the closed chat", async () => {
    state.createCase.mockRejectedValue(httpError(500, "Internal Server Error"));
    render(
      <CaseShellLayout>
        <p>workspace</p>
      </CaseShellLayout>,
    );

    fireEvent.click(screen.getByRole("button", { name: "New case" }));

    expect(await screen.findByRole("dialog")).toHaveTextContent("ระบบไม่สามารถดำเนินการได้");
    expect(localStorage.getItem("cybercase:chat-open")).toBe("false");
  });

  it("shows why the backend refused to start an analysis", async () => {
    state.startAnalysis.mockRejectedValue(
      refusal(
        409,
        "case_sources_changed",
        "The case sources changed while the analysis was running. Analyse again.",
      ),
    );
    render(
      <CaseShellLayout>
        <AnalyzeButton />
      </CaseShellLayout>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));

    const dialog = await screen.findByRole("dialog");
    expect(dialog.querySelector("#meaningful-error-message")).toHaveTextContent(
      "The case sources changed while the analysis was running. Analyse again.",
    );
    fireEvent.click(screen.getAllByRole("button", { name: /ปิด/ })[0]);
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });
});
