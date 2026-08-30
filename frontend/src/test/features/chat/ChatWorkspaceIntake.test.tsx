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
    const threadId = "thread-test-123";
    mockPathname = `/chat/${threadId}/intake`;
    const initialThread: api.PersistedChatThread = {
      id: threadId,
      title: "New case",
      status: "ready",
      created_at: "2026-08-24T06:00:00Z",
      updated_at: "2026-08-24T06:00:00Z",
    };

    vi.spyOn(api, "listChatThreads").mockResolvedValue([initialThread]);
    vi.spyOn(api, "getChatThread").mockResolvedValue({
      thread: initialThread,
      messages: [],
      runs: [],
    });
    vi.spyOn(api, "updateChatThread").mockResolvedValue(initialThread);
    vi.spyOn(api, "listChatReports").mockResolvedValue([]);
    vi.spyOn(api, "createChatMessage").mockRejectedValue(
      new Error("Network error: failed to submit case description"),
    );

    render(
      <QueryClientProvider client={queryClient}>
        <ChatWorkspace initialThreadId={threadId} initialView="intake" />
      </QueryClientProvider>,
    );

    // Wait for thread to load and Intake form to be visible
    await waitFor(() => {
      expect(screen.getByLabelText(/รายละเอียดคดี/i)).toBeInTheDocument();
    });

    const descInput = screen.getByLabelText(/รายละเอียดคดี/i) as HTMLTextAreaElement;
    const titleInput = screen.getByLabelText(/ชื่อคดี/i) as HTMLInputElement;
    const submitBtn = screen.getByRole("button", { name: /Analyze case/i });

    fireEvent.change(titleInput, { target: { value: "IIS Intrusion Case" } });
    fireEvent.change(descInput, {
      target: { value: "PowerShell connected to 198.51.100.23 and downloaded payload." },
    });

    fireEvent.click(submitBtn);

    // Submission failed -> error modal opens with plain-language title, Intake stays mounted, textarea still has content
    await waitFor(() => {
      expect(screen.getByText("ไม่สามารถเชื่อมต่อกับระบบได้")).toBeInTheDocument();
      expect(screen.getByText(/failed to submit case description/i)).toBeInTheDocument();
    });

    expect(screen.getByLabelText(/รายละเอียดคดี/i)).toBeInTheDocument();
    expect(descInput.value).toBe(
      "PowerShell connected to 198.51.100.23 and downloaded payload.",
    );
    expect(titleInput.value).toBe("IIS Intrusion Case");
    // Ensure Overview was NOT navigated to
    expect(mockPush).not.toHaveBeenCalledWith(expect.stringContaining("overview"));
    expect(screen.queryByLabelText("Case Overview")).not.toBeInTheDocument();
  });

  it("navigates to Overview when initial case message submission is accepted", async () => {
    const threadId = "thread-test-456";
    mockPathname = `/chat/${threadId}/intake`;
    const initialThread: api.PersistedChatThread = {
      id: threadId,
      title: "New case",
      status: "ready",
      created_at: "2026-08-24T06:00:00Z",
      updated_at: "2026-08-24T06:00:00Z",
    };

    vi.spyOn(api, "listChatThreads").mockResolvedValue([initialThread]);
    vi.spyOn(api, "getChatThread").mockResolvedValue({
      thread: initialThread,
      messages: [],
      runs: [],
    });
    vi.spyOn(api, "updateChatThread").mockResolvedValue(initialThread);
    vi.spyOn(api, "listChatReports").mockResolvedValue([]);

    const createdMessage: api.PersistedChatMessage = {
      id: "msg-101",
      thread_id: threadId,
      ordinal: 1,
      role: "user",
      content: "PowerShell connected to 198.51.100.23",
      retrieval_context_id: null,
      metadata_json: { evidence_kind: "initial_case_narrative" },
      created_at: "2026-08-24T06:00:00Z",
    };

    const createdRun: api.PersistedChatRun = {
      id: "run-101",
      thread_id: threadId,
      status: "running",
      request_message_ordinal: 1,
      attempt_count: 1,
      lease_expires_at: null,
      recovery_count: 0,
      failure_reason: null,
      created_at: "2026-08-24T06:00:00Z",
      updated_at: "2026-08-24T06:00:00Z",
      completed_at: null,
    };

    vi.spyOn(api, "createChatMessage").mockResolvedValue({
      message: createdMessage,
      run: createdRun,
    });

    vi.spyOn(api, "getChatRun").mockResolvedValue({
      run: { ...createdRun, status: "completed" },
      thread: { ...initialThread, status: "answered" },
      messages: [createdMessage],
    });

    render(
      <QueryClientProvider client={queryClient}>
        <ChatWorkspace initialThreadId={threadId} initialView="intake" />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByLabelText(/รายละเอียดคดี/i)).toBeInTheDocument();
    });

    const descInput = screen.getByLabelText(/รายละเอียดคดี/i) as HTMLTextAreaElement;
    const submitBtn = screen.getByRole("button", { name: /Analyze case/i });

    fireEvent.change(descInput, {
      target: { value: "PowerShell connected to 198.51.100.23" },
    });

    fireEvent.click(submitBtn);

    // Submission accepted -> onAccepted triggers navigation to Overview
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith(`/chat/${threadId}/overview`);
    });
  });
});
