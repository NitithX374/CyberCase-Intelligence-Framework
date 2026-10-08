import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { WorkspaceChatPanel } from "@/features/chat/WorkspaceChatPanel";

const state = vi.hoisted(() => ({ sourcesFailed: false, input: "", submit: vi.fn() }));

vi.mock("@/features/chat/useCaseChat", () => ({
  useCaseChat: () => ({
    messages: [],
    pendingQuestionId: null,
    isSending: false,
    isAnsweringQuestion: false,
    input: state.input,
    changeInput: vi.fn(),
    queryError: null,
    clearQueryError: vi.fn(),
    retryQuery: vi.fn(),
    submitContent: vi.fn(),
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
});

describe("WorkspaceChatPanel", () => {
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
