import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { WorkspaceChatPanel } from "@/features/chat/WorkspaceChatPanel";

const state = vi.hoisted(() => ({ sourcesFailed: false, input: "" }));

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
    submitMessage: vi.fn(),
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

  it("does not call a case empty when its sources failed to load", () => {
    state.sourcesFailed = true;
    renderPanel();
    expect(screen.queryByText("This case has no sources yet.")).not.toBeInTheDocument();
  });
});
