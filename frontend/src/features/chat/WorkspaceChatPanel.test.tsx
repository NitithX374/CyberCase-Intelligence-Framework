import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { WorkspaceChatPanel } from "./WorkspaceChatPanel";

const state = vi.hoisted(() => ({ sourcesFailed: false }));

vi.mock("./useCaseChat", () => ({
  useCaseChat: () => ({
    messages: [],
    pendingQuestionId: null,
    isSending: false,
    isAnsweringQuestion: false,
    input: "",
    changeInput: vi.fn(),
    queryError: null,
    clearQueryError: vi.fn(),
    retryQuery: vi.fn(),
    submitContent: vi.fn(),
    submitMessage: vi.fn(),
  }),
}));
vi.mock("@/features/analysis/queries", () => ({ useCaseAnalysis: () => ({ data: null }) }));
vi.mock("@/features/sources/useCaseSourceRows", () => ({
  useCaseSourceRows: () => ({ caseSources: [], rows: [], isError: state.sourcesFailed }),
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
});

describe("WorkspaceChatPanel", () => {
  it("points an empty case to its sources", () => {
    renderPanel();
    expect(screen.getByText("This case has no sources yet.")).toBeInTheDocument();
  });

  it("does not call a case empty when its sources failed to load", () => {
    state.sourcesFailed = true;
    renderPanel();
    expect(screen.queryByText("This case has no sources yet.")).not.toBeInTheDocument();
  });
});
