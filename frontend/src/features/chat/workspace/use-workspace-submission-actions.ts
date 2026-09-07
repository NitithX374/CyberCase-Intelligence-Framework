"use client";

import { useCallback, type FormEvent } from "react";
import type { CaseIntakeSubmission, CaseNarrativeDocumentSource, ChatMessageAction } from "@/lib/api";
import type { ActiveChatFollowUp } from "@/lib/chat-followup";
import type { WorkspaceRouteView } from "@/components/common/types";
import { chatPath } from "@/features/chat/routing/chat-route";
import type { PendingChatSubmission } from "./chat-workspace-types";
import type { ChatSession } from "./use-chat-thread-selection";

type SubmitContent = (
  content: string,
  kind: PendingChatSubmission["kind"],
  followUp?: ActiveChatFollowUp,
  onAccepted?: () => void,
  documentSources?: CaseNarrativeDocumentSource[],
) => void;

interface WorkspaceSubmissionActionsOptions {
  session: ChatSession;
  displayFollowUp: ActiveChatFollowUp | null;
  router: { push(path: string): void };
  submitContent: SubmitContent;
  updateTitle: (input: { threadId: string; title: string }) => Promise<unknown>;
  setActiveView: React.Dispatch<React.SetStateAction<WorkspaceRouteView>>;
}

export function useWorkspaceSubmissionActions({
  session, displayFollowUp, router, submitContent, updateTitle, setActiveView,
}: WorkspaceSubmissionActionsOptions) {
  const changePostAnswerAction = useCallback((action: ChatMessageAction) => {
    if (session.threadStatus === "answered") session.changePostAnswerAction(action);
  }, [session]);

  const submitMessage = useCallback((event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    submitContent(session.input, displayFollowUp ? "followup" : "message", displayFollowUp ?? undefined);
  }, [displayFollowUp, session.input, submitContent]);

  const submitCase = useCallback(({ title, description, documentSources }: CaseIntakeSubmission) => {
    const threadId = session.getActiveThreadId();
    if (threadId && title) {
      void updateTitle({ threadId, title }).catch(() => {
        if (session.getActiveThreadId() === threadId) session.reportError("The case title could not be updated.");
      });
    }
    submitContent(description, "message", undefined, () => {
      setActiveView("overview");
      const acceptedThreadId = session.getActiveThreadId();
      if (acceptedThreadId !== null) router.push(chatPath(acceptedThreadId, "overview"));
    }, documentSources);
  }, [router, session, setActiveView, submitContent, updateTitle]);

  const clearQueryError = useCallback(() => session.reportError(null), [session]);

  const retryQuery = useCallback(() => {
    const pending = session.getPendingSubmission();
    if (!pending || pending.threadId !== session.getActiveThreadId()) return;
    session.reportError(null);
    submitContent(pending.content, pending.kind, session.pendingFollowUp?.followUp, undefined, pending.documentSources);
  }, [session, submitContent]);

  return { changePostAnswerAction, clearQueryError, retryQuery, submitCase, submitMessage };
}
