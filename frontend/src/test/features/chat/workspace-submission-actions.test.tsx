import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { ActiveChatFollowUp } from "@/lib/chat-followup";
import { useWorkspaceSubmissionActions } from "@/features/chat/workspace/use-workspace-submission-actions";

const followUp: ActiveChatFollowUp = {
  question: "Which host was affected?",
  entries: [],
  rootOrdinal: 1,
};

type SubmitContent = (
  content: string,
  kind: "message" | "followup",
  followUp?: ActiveChatFollowUp,
) => void;

function SubmissionHarness({ submitContent }: { submitContent: SubmitContent }) {
  const actions = useWorkspaceSubmissionActions({
    session: {
      input: "What happened after the login?",
      pendingFollowUp: { threadId: "case-1", followUp },
      getPendingSubmission: () => null,
      getActiveThreadId: () => "case-1",
      reportError: vi.fn(),
    },
    submitContent,
  });

  return (
    <form data-testid="submission-form" onSubmit={actions.submitMessage}>
      <button type="submit">Send</button>
    </form>
  );
}

describe("workspace Chat submission boundary", () => {
  it("keeps an ordinary composer message as Q&A when clarification is displayed", () => {
    const submitContent: SubmitContent = vi.fn();
    render(<SubmissionHarness submitContent={submitContent} />);

    fireEvent.submit(screen.getByTestId("submission-form"));

    expect(submitContent).toHaveBeenCalledWith("What happened after the login?", "message");
  });
});
