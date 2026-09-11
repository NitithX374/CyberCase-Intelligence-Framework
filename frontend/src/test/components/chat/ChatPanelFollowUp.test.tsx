import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ChatPanel } from "@/components/conversation/ChatPanel";
import type { PersistedChatMessage } from "@/lib/api";

const messages: PersistedChatMessage[] = [
  {
    id: "message-1",
    thread_id: "thread-1",
    ordinal: 1,
    role: "user",
    content: "Investigate this PowerShell event.",
    retrieval_context_id: null,
    metadata_json: { evidence_kind: "initial_case_narrative" },
    created_at: "2026-08-23T00:00:00Z",
  },
  {
    id: "message-2",
    thread_id: "thread-1",
    ordinal: 2,
    role: "assistant",
    content: "Which affected host produced this event?",
    retrieval_context_id: "retrieval-1",
    metadata_json: {
      chat_followup: {
        kind: "clarification",
        root_ordinal: 1,
        round: 1,
        selected_gap_detail: {
          topic: "affected host",
          status: "NOT_PROVIDED",
          description: "The affected host was not provided.",
          affects: "The impacted system cannot be scoped.",
          reason: "The reported event has no host identifier.",
          priority: "high",
          askable: true,
        },
      },
    },
    created_at: "2026-08-23T00:00:01Z",
  },
];

describe("ChatPanel boundaries", () => {
  it("renders the persisted clarification and enables composer to answer in Chat", () => {
    Element.prototype.scrollIntoView = vi.fn();
    const onInputChange = vi.fn();

    render(
      <ChatPanel
        messages={messages}
        input="host-7"
        threadStatus="awaiting_followup"
        phase="awaiting_followup"
        hasAnalysisContext
        onInputChange={onInputChange}
        onSubmit={vi.fn()}
      />,
    );

    expect(
      screen.getByText("Which affected host produced this event?"),
    ).toBeInTheDocument();
    expect(screen.getByText("affected host")).toBeInTheDocument();
    const composer = screen.getByLabelText("Chat message");
    expect(screen.getByText("Clarification needed")).toBeInTheDocument();
    expect(screen.getByText(/Provide your answer below to resume the case analysis/i)).toBeInTheDocument();
    expect(composer).not.toBeDisabled();
    expect(screen.getByRole("button", { name: "Send message" })).not.toBeDisabled();

    fireEvent.change(composer, { target: { value: "host-9" } });
    expect(onInputChange).toHaveBeenCalledWith("host-9");
  });

  it("explains that Chat has no context before Case analysis", () => {
    render(
      <ChatPanel
        messages={[]}
        input=""
        threadStatus="idle"
        phase="idle"
        hasAnalysisContext={false}
        onInputChange={vi.fn()}
        onSubmit={vi.fn()}
      />,
    );

    expect(screen.getByText(/Complete the Case analysis from Intake before using Chat/i)).toBeInTheDocument();
    expect(screen.getByText(/Chat will not start analysis/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Chat message")).toBeDisabled();
  });
});
