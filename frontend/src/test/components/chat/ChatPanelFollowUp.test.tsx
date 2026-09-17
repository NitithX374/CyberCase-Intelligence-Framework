import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { WorkspaceChatPanel } from "@/components/conversation/WorkspaceChatPanel";
import type { ChatMessageRead } from "@/lib/api";
import type { ActiveChatFollowUp } from "@/lib/chat-followup";

const messages: ChatMessageRead[] = [
  {
    id: "message-1",
    case_id: "caseChat-1",
    ordinal: 1,
    role: "user",
    content: "Investigate this PowerShell event.",
    retrieval_context_id: null,
    message_kind: "conversation",
    analysis_result_id: null,
    metadata_json: {},
    created_at: "2026-08-23T00:00:00Z",
  },
  {
    id: "message-2",
    case_id: "caseChat-1",
    ordinal: 2,
    role: "assistant",
    content: "Which affected host produced this event?",
    retrieval_context_id: "retrieval-1",
    message_kind: "followup_question",
    analysis_result_id: null,
    metadata_json: {
      action: "follow_up",
      chat_followup: {
        root_ordinal: 1,
        round: 1,
        source_analysis_id: "analysis-1",
        source_revision: 1,
        gap: {
          gap_id: "gap-host",
          gap_key: "affected_host",
          topic: "affected host",
          status: "NOT_PROVIDED",
          description: "The affected host was not provided.",
          affects: "The impacted system cannot be scoped.",
          reason: "The reported event has no host identifier.",
          priority: "high",
          askable: true,
          clarification_question: "Which affected host produced this event?",
        },
      },
    },
    created_at: "2026-08-23T00:00:01Z",
  },
];

const pendingFollowUp: ActiveChatFollowUp = {
  question: "Which affected host produced this event?",
  gap: {
    gapId: "gap-host",
    gapKey: "affected_host",
    topic: "affected host",
    status: "NOT_PROVIDED",
    description: "The affected host was not provided.",
    affects: "The impacted system cannot be scoped.",
    reason: "The reported event has no host identifier.",
    priority: "high",
    askable: true,
    question: "Which affected host produced this event?",
  },
  entries: [],
  rootOrdinal: 1,
  round: 1,
  questionMessageId: "message-2",
  sourceAnalysisId: "analysis-1",
  sourceRevision: 1,
};

describe("WorkspaceChatPanel boundaries", () => {
  it("renders the persisted clarification and enables composer to answer in Chat", () => {
    Element.prototype.scrollIntoView = vi.fn();
    const onInputChange = vi.fn();
    const onSubmit = vi.fn();
    const onSubmitFollowUp = vi.fn();

    render(
      <WorkspaceChatPanel
        isOpen
        messages={messages}
        visibleMessages={messages}
        input="host-7"
        chatStatus="awaiting_followup"
        phase="awaiting_followup"
        hasAnalysisContext
        onViewChange={vi.fn()}
        onInputChange={onInputChange}
        onSubmit={onSubmit}
        pendingFollowUp={pendingFollowUp}
        onSubmitFollowUp={onSubmitFollowUp}
      />,
    );

    expect(
      screen.getByText("Which affected host produced this event?"),
    ).toBeInTheDocument();
    expect(screen.getAllByText("affected host").length).toBeGreaterThanOrEqual(2);
    const composer = screen.getByLabelText("Chat message");
    expect(screen.getByText("One gap remains:")).toBeInTheDocument();
    fireEvent.submit(composer.closest("form")!);
    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmitFollowUp).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Clarify this gap" }));
    expect(screen.getByText("Clarification round 1")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continue with Ask" })).toBeInTheDocument();
    expect(composer).not.toBeDisabled();
    expect(screen.getByRole("button", { name: "Send message" })).not.toBeDisabled();

    fireEvent.change(composer, { target: { value: "host-9" } });
    expect(onInputChange).toHaveBeenCalledWith("host-9");
  });

  it("shows intake notice and keeps composer available before Case analysis", () => {
    render(
      <WorkspaceChatPanel
        isOpen
        messages={[]}
        visibleMessages={[]}
        input=""
        chatStatus="idle"
        phase="idle"
        hasAnalysisContext={false}
        onViewChange={vi.fn()}
        onInputChange={vi.fn()}
        onSubmit={vi.fn()}
      />,
    );

    expect(screen.getByText(/ยังไม่ได้บันทึกรายละเอียดสำนวนคดี/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Chat message")).not.toBeDisabled();
  });
});
