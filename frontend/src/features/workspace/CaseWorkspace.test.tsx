import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { AnalysisStepRead } from "@/lib/api/types";
import { useRunCaseAnalysis } from "@/features/analysis/useRunCaseAnalysis";
import { deferred } from "@/features/chat/chatTestSupport";
import { analysisResult, caseId } from "@/test/fixtures";
import { httpError, refusal } from "@/test/httpErrors";
import { CaseWorkspace } from "./CaseWorkspace";

const state = vi.hoisted(() => ({
  createCase: vi.fn(),
  push: vi.fn(),
  start: vi.fn(),
  segment: "sources" as string | null,
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ caseId }),
  useRouter: () => ({ push: state.push, replace: vi.fn() }),
  useSelectedLayoutSegment: () => state.segment,
}));
vi.mock("@/features/analysis/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/analysis/api")>()),
  startCaseAnalysis: (...args: unknown[]) => state.start(...args),
}));
vi.mock("@/features/cases/queries", () => ({
  useCase: () => ({ data: undefined }),
  useCaseMutations: () => ({
    createMutation: { isPending: false, mutateAsync: state.createCase },
    updateMutation: { isPending: false, mutateAsync: vi.fn() },
  }),
}));
vi.mock("@/features/workspace/WorkspaceHeader", () => ({
  WorkspaceHeader: ({ activeView, onNewCase }: { activeView: string; onNewCase: () => void }) => (
    <>
      <p>Viewing {activeView}</p>
      <button type="button" onClick={onNewCase}>
        New case
      </button>
    </>
  ),
}));
vi.mock("@/features/chat/WorkspaceChatPanel", () => ({
  WorkspaceChatPanel: ({ isOpen, onCloseChat }: { isOpen: boolean; onCloseChat: () => void }) =>
    isOpen ? (
      <aside aria-label="Ask about this case">
        <p>When did the incident happen?</p>
        <button type="button" onClick={onCloseChat}>
          Close Ask
        </button>
      </aside>
    ) : null,
}));

const QUESTION: AnalysisStepRead = { status: "need_followup" };

function AnalyzeButton() {
  const runAnalysis = useRunCaseAnalysis(caseId);
  return (
    <button type="button" onClick={runAnalysis}>
      Analyze
    </button>
  );
}

function renderLayout(page: ReactNode = <p>workspace</p>) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const layout = (children: ReactNode) => (
    <QueryClientProvider client={queryClient}>
      <CaseWorkspace>{children}</CaseWorkspace>
    </QueryClientProvider>
  );
  const view = render(layout(page));
  return { showPage: (next: ReactNode) => view.rerender(layout(next)) };
}

const ask = () => screen.queryByRole("complementary", { name: "Ask about this case" });

beforeEach(() => {
  state.createCase.mockReset();
  state.push.mockReset();
  state.start.mockReset();
  state.segment = "sources";
  localStorage.clear();
});

describe("CaseWorkspace", () => {
  it("tells the reader when a new case could not be created, and remembers the closed chat", async () => {
    state.createCase.mockRejectedValue(httpError(500, "Internal Server Error"));
    renderLayout();

    fireEvent.click(screen.getByRole("button", { name: "New case" }));

    expect(await screen.findByRole("dialog")).toHaveTextContent("ระบบไม่สามารถดำเนินการได้");
    expect(localStorage.getItem("cybercase:chat-open")).toBe("false");
  });

  it("reads the open view from the route", () => {
    renderLayout();
    expect(screen.getByText("Viewing sources")).toBeInTheDocument();
  });

  it("treats the case root as Analysis", () => {
    state.segment = null;
    renderLayout();
    expect(screen.getByText("Viewing analysis")).toBeInTheDocument();
  });
});

describe("an analysis run started from a page", () => {
  it("goes to the analysis once it is written, and leaves the language to the backend", async () => {
    state.start.mockResolvedValue({ status: "completed", result: analysisResult() });
    renderLayout(<AnalyzeButton />);

    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));

    await waitFor(() => expect(state.push).toHaveBeenCalledWith(`/case/${caseId}/analysis`));
    expect(state.start).toHaveBeenCalledWith(caseId);
  });

  it("says in Thai why it failed, after the reader has left the page that started it", async () => {
    const run = deferred<AnalysisStepRead>();
    state.start.mockReturnValue(run.promise);
    const { showPage } = renderLayout(<AnalyzeButton />);

    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    await waitFor(() => expect(state.start).toHaveBeenCalledOnce());
    showPage(<p>legal</p>);
    expect(screen.queryByRole("button", { name: "Analyze" })).not.toBeInTheDocument();

    await act(async () =>
      run.reject(
        refusal(
          409,
          "case_sources_changed",
          "The case sources changed while the analysis was running. Analyse again.",
        ),
      ),
    );

    const dialog = await screen.findByRole("dialog");
    expect(dialog.querySelector("#meaningful-error-message")).toHaveTextContent(
      "แหล่งข้อมูลของคดีเปลี่ยนไประหว่างการวิเคราะห์ กรุณาวิเคราะห์อีกครั้ง",
    );
    expect(state.push).not.toHaveBeenCalled();
  });

  it("opens Ask every time it asks, even when the question is one Ask already showed", async () => {
    localStorage.setItem("cybercase:chat-open", "false");
    state.start.mockResolvedValue(QUESTION);
    renderLayout(<AnalyzeButton />);
    expect(ask()).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    await waitFor(() => expect(ask()).toBeInTheDocument());

    fireEvent.click(screen.getByRole("button", { name: "Close Ask" }));
    expect(ask()).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    await waitFor(() => expect(ask()).toBeInTheDocument());
    expect(state.start).toHaveBeenCalledTimes(2);
    expect(state.push).not.toHaveBeenCalled();
  });
});
