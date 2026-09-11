import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ChatWorkspace } from "@/components/ChatWorkspace";
import * as api from "@/lib/api";

let mockPathname = "/chat/thread-test-123/intake";
const mockPush = vi.fn((path: string) => {
  mockPathname = path;
});

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => mockPathname,
}));

describe("ChatWorkspace Intake submission integration", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    mockPathname = "/chat/thread-test-123/intake";
    mockPush.mockClear();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.restoreAllMocks();
  });

  it("preserves draft narrative and keeps Intake mounted when message submission fails", async () => {
    const caseId = "case-test-123";
    mockPathname = `/case/${caseId}/intake`;
    const initialCase: api.CaseRead = {
      id: caseId,
      title: "New case",
      status: "idle",
      chat_thread_id: null,
      evidence_revision: 0,
      created_at: "2026-08-24T06:00:00Z",
      updated_at: "2026-08-24T06:00:00Z",
    };

    vi.spyOn(api, "listCases").mockResolvedValue([initialCase]);
    vi.spyOn(api, "listCaseDocuments").mockResolvedValue([]);
    vi.spyOn(api, "listCaseEvidence").mockResolvedValue([]);
    vi.spyOn(api, "getCaseAnalysis").mockResolvedValue(null);
    vi.spyOn(api, "listCaseClarifications").mockResolvedValue([]);
    vi.spyOn(api, "getCase").mockResolvedValue(initialCase);
    vi.spyOn(api, "updateCase").mockResolvedValue(initialCase);
    vi.spyOn(api, "admitCaseEvidence").mockRejectedValue(
      new Error("Network error: failed to submit case description"),
    );

    render(
      <QueryClientProvider client={queryClient}>
        <ChatWorkspace />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByLabelText(/Case narrative/i)).toBeInTheDocument();
    });

    const descInput = screen.getByLabelText(/Case narrative/i) as HTMLTextAreaElement;
    const titleInput = screen.getByLabelText(/Case title/i) as HTMLInputElement;
    const submitBtn = screen.getByRole("button", { name: /Analyze case/i });

    fireEvent.change(titleInput, { target: { value: "IIS Intrusion Case" } });
    fireEvent.change(descInput, {
      target: { value: "PowerShell connected to 198.51.100.23 and downloaded payload." },
    });

    await waitFor(() => {
      expect(submitBtn).not.toBeDisabled();
    });

    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("ไม่สามารถเชื่อมต่อกับระบบได้")).toBeInTheDocument();
      expect(screen.getAllByText(/failed to submit case description/i).length).toBeGreaterThan(0);
    });

    expect(screen.getByLabelText(/Case narrative/i)).toBeInTheDocument();
    expect(descInput.value).toBe(
      "PowerShell connected to 198.51.100.23 and downloaded payload.",
    );
    expect(titleInput.value).toBe("IIS Intrusion Case");
    expect(mockPush).not.toHaveBeenCalledWith(expect.stringContaining("overview"));
    expect(screen.queryByLabelText("Case Overview")).not.toBeInTheDocument();
  });

  it("navigates to Overview when initial case message submission is accepted", async () => {
    const caseId = "case-test-456";
    mockPathname = `/case/${caseId}/intake`;
    const initialCase: api.CaseRead = {
      id: caseId,
      title: "New case",
      status: "idle",
      chat_thread_id: null,
      evidence_revision: 0,
      created_at: "2026-08-24T06:00:00Z",
      updated_at: "2026-08-24T06:00:00Z",
    };
    const admittedCase = { ...initialCase, evidence_revision: 1 };

    vi.spyOn(api, "listCases").mockResolvedValue([initialCase]);
    vi.spyOn(api, "listCaseDocuments").mockResolvedValue([]);
    vi.spyOn(api, "listCaseEvidence").mockResolvedValue([]);
    vi.spyOn(api, "getCaseAnalysis").mockResolvedValue(null);
    vi.spyOn(api, "listCaseClarifications").mockResolvedValue([]);
    vi.spyOn(api, "getCase").mockResolvedValueOnce(initialCase).mockResolvedValue(admittedCase);
    vi.spyOn(api, "admitCaseEvidence").mockResolvedValue({} as Awaited<ReturnType<typeof api.admitCaseEvidence>>);
    vi.spyOn(api, "updateCase").mockResolvedValue(initialCase);
    const createdRun: api.CaseRunRead = {
      id: "run-101",
      case_id: caseId,
      operation: "analysis",
      snapshot_id: "snapshot-101",
      request_message_id: null,
      context_analysis_result_id: null,
      clarification_id: null,
      status: "queued",
      attempt_count: 0,
      error_code: null,
      error_message: null,
      created_at: "2026-08-24T06:00:00Z",
      started_at: null,
      finished_at: null,
      updated_at: "2026-08-24T06:00:00Z",
    };

    vi.spyOn(api, "startCaseAnalysis").mockResolvedValue({ run: createdRun });
    vi.spyOn(api, "getCaseRun").mockResolvedValue({ ...createdRun, status: "completed" });
    render(
      <QueryClientProvider client={queryClient}>
        <ChatWorkspace />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByLabelText(/Case narrative/i)).toBeInTheDocument();
    });

    const descInput = screen.getByLabelText(/Case narrative/i) as HTMLTextAreaElement;
    const submitBtn = screen.getByRole("button", { name: /Analyze case/i });

    fireEvent.change(descInput, {
      target: { value: "PowerShell connected to 198.51.100.23" },
    });

    await waitFor(() => {
      expect(submitBtn).not.toBeDisabled();
    });

    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith(`/case/${caseId}/overview`);
    });
  });
});
