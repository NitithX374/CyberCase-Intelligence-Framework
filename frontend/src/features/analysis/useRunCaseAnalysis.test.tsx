import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider, useMutation } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";
import type { CaseChatResponse } from "@/lib/api/types";
import { useCaseChat } from "@/features/chat/useCaseChat";
import { caseChat, chatResponse, deferred, message } from "@/test/chat";
import { useAnalysisRunOutcome, useRunCaseAnalysis } from "./useRunCaseAnalysis";

const api = vi.hoisted(() => ({ getChat: vi.fn(), send: vi.fn(), start: vi.fn() }));

vi.mock("@/features/chat/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/chat/api")>()),
  getCaseChat: (...args: unknown[]) => api.getChat(...args),
  createCaseChatMessage: (...args: unknown[]) => api.send(...args),
}));

vi.mock("./api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./api")>()),
  startCaseAnalysis: (...args: unknown[]) => api.start(...args),
}));

function Listener() {
  useAnalysisRunOutcome("case-1", {
    onCompleted: vi.fn(),
    onQuestion: vi.fn(),
    onFailed: vi.fn(),
  });
  return null;
}

function LaterMutation() {
  useMutation({ mutationFn: async () => null });
  return null;
}

describe("useAnalysisRunOutcome", () => {
  it("lets another component mount a mutation while it listens", () => {
    const client = new QueryClient();
    const { rerender } = render(
      <QueryClientProvider client={client}>
        <Listener />
      </QueryClientProvider>,
    );

    expect(() =>
      rerender(
        <QueryClientProvider client={client}>
          <Listener />
          <LaterMutation />
        </QueryClientProvider>,
      ),
    ).not.toThrow();
  });
});

function AnswerThenAnalyze() {
  const chat = useCaseChat({ caseId: "case-1" });
  const runAnalysis = useRunCaseAnalysis("case-1");
  return (
    <>
      <p>Waiting on {chat.pendingQuestionId ?? "nothing"}</p>
      <button type="button" onClick={() => chat.submitContent("Around 02:00.")}>
        Answer
      </button>
      <button type="button" onClick={runAnalysis}>
        Analyze
      </button>
    </>
  );
}

describe("useRunCaseAnalysis", () => {
  it("does not start an analysis while an answer to a question is being analysed", async () => {
    const question = {
      ...message("case-1", 1, "assistant", "When did it start?"),
      message_kind: "followup_question" as const,
      gap_key: "topic:incident-time",
    };
    api.getChat.mockResolvedValue(caseChat("case-1", [question], question.id));
    const answering = deferred<CaseChatResponse>();
    api.send.mockReturnValue(answering.promise);
    api.start.mockResolvedValue({ status: "need_followup" });
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={client}>
        <AnswerThenAnalyze />
      </QueryClientProvider>,
    );

    expect(await screen.findByText(`Waiting on ${question.id}`)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Answer" }));
    await waitFor(() => expect(api.send).toHaveBeenCalledOnce());
    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    await act(async () => {});
    expect(api.start).not.toHaveBeenCalled();

    await act(async () => answering.resolve(chatResponse()));
    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    await waitFor(() => expect(api.start).toHaveBeenCalledOnce());
  });
});
