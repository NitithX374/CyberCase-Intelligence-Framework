import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { WorkspaceChatPanel } from "@/features/chat/WorkspaceChatPanel";
import type { ChatMessageRead } from "@/lib/api/types";
import { followupExchange } from "@/test/fixtures";

const state = vi.hoisted(() => ({
  sourcesFailed: false,
  input: "",
  submit: vi.fn(),
  submitContent: vi.fn(),
  messages: [] as ChatMessageRead[],
  pendingQuestionId: null as string | null,
}));

vi.mock("@/features/chat/useCaseChat", () => ({
  useCaseChat: () => ({
    messages: state.messages,
    pendingQuestionId: state.pendingQuestionId,
    isSending: false,
    isAnsweringQuestion: false,
    input: state.input,
    changeInput: vi.fn(),
    queryError: null,
    clearQueryError: vi.fn(),
    retryQuery: vi.fn(),
    submitContent: state.submitContent,
    submitMessage: state.submit,
  }),
}));
vi.mock("@/features/analysis/queries", () => ({ useCaseAnalysis: () => ({ data: null }) }));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () =>
    state.sourcesFailed
      ? { data: undefined, isLoadingError: true }
      : { data: [], isLoadingError: false },
}));

function renderPanel() {
  render(
    <WorkspaceChatPanel
      caseId="case-1"
      isOpen
      onOpenChat={vi.fn()}
      onCloseChat={vi.fn()}
      onViewChange={vi.fn()}
    />,
  );
}

beforeEach(() => {
  state.sourcesFailed = false;
  state.input = "";
  state.submit.mockReset();
  state.submitContent.mockReset();
  state.messages = [];
  state.pendingQuestionId = null;
});

describe("WorkspaceChatPanel", () => {
  it("says above the input which question is being answered", () => {
    const [question] = followupExchange("Who did it?", "", "who_responsible");
    state.messages = [question];
    state.pendingQuestionId = question.id;
    renderPanel();
    expect(screen.getByText("Answering question 1")).toBeInTheDocument();
    expect(screen.getByLabelText("Chat message")).toHaveAttribute(
      "placeholder",
      "Type your answer…",
    );
  });

  it("skips a question by answering that it is not known, in the question's language", () => {
    const [question] = followupExchange("ใครเป็นผู้กระทำ?", "", "who_responsible");
    state.messages = [question];
    state.pendingQuestionId = question.id;
    renderPanel();
    fireEvent.click(screen.getByRole("button", { name: "Don't know" }));
    expect(state.submitContent).toHaveBeenCalledWith("ไม่ทราบ");
  });

  it("points an empty case to its sources", () => {
    renderPanel();
    expect(screen.getByText("This case has no sources yet.")).toBeInTheDocument();
  });

  it("accepts a message of exactly the length the backend accepts", () => {
    state.input = "a".repeat(4_000);
    renderPanel();

    expect(screen.getByRole("button", { name: "Send message" })).toBeEnabled();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("refuses a longer message and says so, instead of cutting it", () => {
    state.input = "a".repeat(4_001);
    renderPanel();

    expect(screen.getByLabelText("Chat message")).not.toHaveAttribute("maxlength");
    expect(screen.getByRole("button", { name: "Send message" })).toBeDisabled();
    expect(screen.getByRole("status")).toHaveTextContent("4,001 of 4,000 characters");
  });

  describe("sending from the keyboard", () => {
    const press = (init: KeyboardEventInit) =>
      fireEvent.keyDown(screen.getByLabelText("Chat message"), { key: "Enter", ...init });

    it("sends on Enter, and the button says so", () => {
      state.input = "What happened?";
      renderPanel();

      const notPrevented = press({});

      expect(notPrevented).toBe(false);
      expect(state.submit).toHaveBeenCalledTimes(1);
      expect(screen.getByRole("button", { name: "Send message" })).toHaveAttribute(
        "title",
        "Send (Enter)",
      );
    });

    it("still sends on Ctrl+Enter and Cmd+Enter", () => {
      state.input = "What happened?";
      renderPanel();

      press({ ctrlKey: true });
      press({ metaKey: true });

      expect(state.submit).toHaveBeenCalledTimes(2);
    });

    it("leaves Shift+Enter to make a new line", () => {
      state.input = "What happened?";
      renderPanel();

      const notPrevented = press({ shiftKey: true });

      expect(notPrevented).toBe(true);
      expect(state.submit).not.toHaveBeenCalled();
    });

    it("does not send while an input method is composing text", () => {
      state.input = "What happened?";
      renderPanel();

      const notPrevented = press({ isComposing: true });

      expect(notPrevented).toBe(true);
      expect(state.submit).not.toHaveBeenCalled();
    });

    it("sends nothing for a blank message, and adds no blank line", () => {
      state.input = "   ";
      renderPanel();

      const notPrevented = press({});

      expect(notPrevented).toBe(false);
      expect(state.submit).not.toHaveBeenCalled();
    });

    it("does not send a message the button would refuse as too long", () => {
      state.input = "a".repeat(4_001);
      renderPanel();

      press({});
      press({ ctrlKey: true });

      expect(state.submit).not.toHaveBeenCalled();
    });

    it("ignores other keys", () => {
      state.input = "What happened?";
      renderPanel();

      fireEvent.keyDown(screen.getByLabelText("Chat message"), { key: "a" });

      expect(state.submit).not.toHaveBeenCalled();
    });
  });

  it("does not call a case empty when its sources failed to load", () => {
    state.sourcesFailed = true;
    renderPanel();
    expect(screen.queryByText("This case has no sources yet.")).not.toBeInTheDocument();
  });
});
