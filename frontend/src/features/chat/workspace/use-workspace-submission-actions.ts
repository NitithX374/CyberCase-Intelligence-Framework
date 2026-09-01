"use client";

import { useCallback, type FormEvent } from "react";
import type {
  CaseIntakeSubmission,
  CaseNarrativeDocumentSource,
  ChatMessageAction,
  ChatThreadRead,
} from "@/lib/api";
import type { ActiveChatFollowUp } from "@/lib/chat-followup";
import type { WorkspaceRouteView } from "@/components/common/types";
import { chatPath } from "@/features/chat/routing/chat-route";
import type { PendingChatSubmission } from "./chat-workspace-types";

type SubmitContent = (
  content: string,
  kind: PendingChatSubmission["kind"],
  followUp?: ActiveChatFollowUp,
  onAccepted?: () => void,
  documentSources?: CaseNarrativeDocumentSource[],
) => void;

interface WorkspaceSubmissionActionsOptions {
  activeThreadIdRef: React.MutableRefObject<string | null>;
  pendingSubmissionRef: React.MutableRefObject<PendingChatSubmission | null>;
  pendingFollowUp: { threadId: string; followUp: ActiveChatFollowUp } | null;
  displayFollowUp: ActiveChatFollowUp | null;
  input: string;
  threadStatus: ChatThreadRead["status"] | null;
  router: { push(path: string): void };
  submitContent: SubmitContent;
  updateTitle: (input: { threadId: string; title: string }) => Promise<unknown>;
  setActiveView: React.Dispatch<React.SetStateAction<WorkspaceRouteView>>;
  setPostAnswerAction: React.Dispatch<React.SetStateAction<ChatMessageAction | null>>;
  setQueryError: React.Dispatch<React.SetStateAction<string | null>>;
}

export function useWorkspaceSubmissionActions({
  activeThreadIdRef,
  pendingSubmissionRef,
  pendingFollowUp,
  displayFollowUp,
  input,
  threadStatus,
  router,
  submitContent,
  updateTitle,
  setActiveView,
  setPostAnswerAction,
  setQueryError,
}: WorkspaceSubmissionActionsOptions) {
  const changePostAnswerAction = useCallback(
    (action: ChatMessageAction) => {
      if (threadStatus === "answered") setPostAnswerAction(action);
    },
    [setPostAnswerAction, threadStatus],
  );

  const submitMessage = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      submitContent(
        input,
        displayFollowUp ? "followup" : "message",
        displayFollowUp ?? undefined,
      );
    },
    [displayFollowUp, input, submitContent],
  );

  const submitCase = useCallback(
    ({ title, description, documentSources }: CaseIntakeSubmission) => {
      const threadId = activeThreadIdRef.current;
      if (threadId && title) {
        void updateTitle({ threadId, title }).catch(() => undefined);
      }
      submitContent(
        description,
        "message",
        undefined,
        () => {
          setActiveView("overview");
          if (threadId !== null) router.push(chatPath(threadId, "overview"));
        },
        documentSources,
      );
    },
    [activeThreadIdRef, router, setActiveView, submitContent, updateTitle],
  );

  const clearQueryError = useCallback(() => {
    setQueryError(null);
  }, [setQueryError]);

  const retryQuery = useCallback(() => {
    const pending = pendingSubmissionRef.current;
    setQueryError(null);
    if (!pending) return;
    submitContent(
      pending.content,
      pending.kind,
      pendingFollowUp?.followUp,
      undefined,
      pending.documentSources,
    );
  }, [pendingFollowUp, pendingSubmissionRef, setQueryError, submitContent]);

  return {
    changePostAnswerAction,
    clearQueryError,
    retryQuery,
    submitCase,
    submitMessage,
  };
}
