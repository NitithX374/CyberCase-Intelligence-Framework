import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "@/lib/api";
import { useCaseWorkspaceActions } from "@/hooks/useCaseWorkspaceActions";
import type { CaseRead, CaseRunRead } from "@/lib/api";
import type { ChatSession } from "@/features/chat/workspace/use-chat-thread-selection";

vi.mock("@/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/api")>();
  return {
    ...actual,
    admitCaseEvidence: vi.fn(),
    admitCaseDocument: vi.fn(),
    answerCaseClarification: vi.fn(),
    ensureCaseChat: vi.fn(),
    getCase: vi.fn(),
    startCaseAnalysis: vi.fn(),
    uploadCaseDocument: vi.fn(),
  };
});

const initialCase: CaseRead = {
  id: "case-1",
  user_id: null,
  title: "Untitled Case",
  status: "idle",
  chat_thread_id: null,
  evidence_revision: 0,
  latest_analysis_result_id: null,
  active_run_id: null,
  latest_run_id: null,
  processing_status: "idle",
  analysis_freshness: "missing",
  created_at: "2026-09-10T01:00:00Z",
  updated_at: "2026-09-10T01:00:00Z",
};

const admittedCase: CaseRead = {
  ...initialCase,
  evidence_revision: 1,
};

const acceptedRun: CaseRunRead = {
  id: "run-1",
  case_id: "case-1",
  operation: "analysis",
  snapshot_id: "snapshot-1",
  request_message_id: null,
  context_analysis_result_id: null,
  clarification_id: null,
  status: "queued",
  attempt_count: 0,
  error_code: null,
  error_message: null,
  created_at: "2026-09-10T01:01:00Z",
  started_at: null,
  finished_at: null,
  updated_at: "2026-09-10T01:01:00Z",
};

function wrapper({ children }: PropsWithChildren) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe("useCaseWorkspaceActions", () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem("cybercase:account", "analyst-a");
    vi.mocked(api.getCase).mockReset();
    vi.mocked(api.admitCaseEvidence).mockReset();
    vi.mocked(api.startCaseAnalysis).mockReset();
    vi.mocked(api.getCase).mockResolvedValueOnce(initialCase).mockResolvedValue(admittedCase);
    vi.mocked(api.admitCaseEvidence).mockResolvedValue({} as Awaited<ReturnType<typeof api.admitCaseEvidence>>);
    vi.mocked(api.startCaseAnalysis)
      .mockRejectedValueOnce(new Error("request timed out"))
      .mockResolvedValue({ run: acceptedRun });
  });

  it("reuses the admitted evidence and logical Analyze identity after an uncertain response", async () => {
    const session = {
      clearSelection: vi.fn(),
      selectThread: vi.fn(),
    } as unknown as ChatSession;
    const { result } = renderHook(
      () => useCaseWorkspaceActions({
        activeCaseId: "case-1",
        activeCase: initialCase,
        isChatOpen: false,
        setIsChatOpen: vi.fn(),
        session,
        upsertCase: vi.fn(),
        updateCase: vi.fn().mockResolvedValue(initialCase),
        router: { push: vi.fn() },
        setActiveView: vi.fn(),
      }),
      { wrapper },
    );

    const submission = { title: "Incident review", description: "The witness reported a blue vehicle." };
    await act(async () => {
      await result.current.submitCase(submission);
    });
    await waitFor(() => expect(result.current.isSubmitting).toBe(false));
    await act(async () => {
      await result.current.submitCase(submission);
    });

    expect(api.admitCaseEvidence).toHaveBeenCalledOnce();
    expect(api.startCaseAnalysis).toHaveBeenCalledTimes(2);
    const firstRequest = vi.mocked(api.startCaseAnalysis).mock.calls[0]?.[1];
    const secondRequest = vi.mocked(api.startCaseAnalysis).mock.calls[1]?.[1];
    expect(secondRequest?.idempotency_key).toBe(firstRequest?.idempotency_key);
    expect(firstRequest?.expected_evidence_revision).toBe(1);
    expect(secondRequest?.expected_evidence_revision).toBe(1);
  });
});
