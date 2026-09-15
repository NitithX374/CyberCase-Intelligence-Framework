"use client";

import { useCallback, type FormEvent } from "react";
import type { ActiveChatFollowUp } from "@/lib/chat-followup";
import type { PendingChatSubmission } from "./chat-workspace-types";
import type { CaseChatSession } from "./use-case-chat-selection";

type SubmitContent = (
  content: string,
  kind: PendingChatSubmission["kind"],
  followUp?: ActiveChatFollowUp,
) => void;

interface WorkspaceSubmissionActionsOptions {
  session: Pick<CaseChatSession, "input" | "pendingFollowUp" | "getPendingSubmission" | "getActiveCaseChatId" | "reportError">;
  submitContent: SubmitContent;
}

export function useWorkspaceSubmissionActions({
  session, submitContent,
}: WorkspaceSubmissionActionsOptions) {
  const submitMessage = useCallback((event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    submitContent(session.input, "message");
  }, [session.input, submitContent]);

  const clearQueryError = useCallback(() => session.reportError(null), [session]);

  const retryQuery = useCallback(() => {
    const pending = session.getPendingSubmission();
    if (!pending || pending.caseId !== session.getActiveCaseChatId()) return;
    session.reportError(null);
    submitContent(pending.content, pending.kind, session.pendingFollowUp?.followUp);
  }, [session, submitContent]);

  return { clearQueryError, retryQuery, submitMessage };
}
