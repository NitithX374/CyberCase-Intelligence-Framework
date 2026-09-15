"use client";

import { useCallback, useRef } from "react";
import {
  createCaseChatMessage, getApiErrorMessage,
  type CaseRead,
} from "@/lib/api";
import { hasCompletedAssistantOutput, type ActiveChatFollowUp } from "@/lib/chat-followup";
import { isChatRequestCanceled } from "./chat-polling";
import type { PendingChatSubmission } from "../workspace/chat-workspace-types";
import type { CaseChatSelection, CaseChatSession } from "../workspace/use-case-chat-selection";

interface UseCaseChatSubmissionOptions {
  session: CaseChatSession;
  cases: CaseRead[];
  upsertCase: (caseRecord: CaseRead) => void;
  caseId: string | null;
}

export function useCaseChatSubmission({
  session, cases, upsertCase, caseId,
}: UseCaseChatSubmissionOptions) {
  const submissionsRef = useRef(new Set<CaseChatSelection | null>());
  const submitContent = useCallback((
    rawContent: string,
    kind: PendingChatSubmission["kind"],
    followUp?: ActiveChatFollowUp,
  ) => {
    if (caseId === null) {
      session.reportError("Open a Case before sending a message.");
      return;
    }
    if (session.phase === "querying" || session.phase === "analyzing") return;
    const content = rawContent.trim();
    const saved = session.getPendingSubmission();
    const savedRetry = saved?.caseId === session.getActiveCaseChatId() &&
      saved.content === content && saved.kind === kind ? saved : null;
    if (!content || (kind === "followup" && !followUp && !savedRetry)) return;
    const initialSelection = session.getSelection();
    if (submissionsRef.current.has(initialSelection)) return;
    const currentCase = cases.find((caseRecord) => caseRecord.id === caseId);
    const statusBeforeSubmit = session.chatStatus;
    const isAwaitingClarification = Boolean(
      currentCase?.has_pending_clarification ||
      currentCase?.status === "awaiting_followup" ||
      statusBeforeSubmit === "awaiting_followup"
    );
    const isAnsweringFollowUp = kind === "followup" || isAwaitingClarification;
    const submissionKind = isAnsweringFollowUp ? "followup" : kind;
    submissionsRef.current.add(initialSelection);

    void (async () => {
      try {
        const selection = initialSelection;
        if (!selection || !session.isCurrentSelection(selection)) return;
        const pending = session.getPendingSubmission();
        const samePending = pending?.caseId === caseId &&
          pending.content === content && pending.kind === submissionKind;
        const submission: PendingChatSubmission = samePending && pending ? pending : {
          caseId, content, key: window.crypto.randomUUID(), kind: submissionKind,
          lastKnownMessageOrdinal: session.messages.reduce((ordinal, message) => Math.max(ordinal, message.ordinal), 0),
        };
        session.beginSubmission(submission, followUp);
        const answeredQuestionIds = new Set(
          session.messages
            .map((m) => m.in_reply_to_message_id)
            .filter(Boolean),
        );
        const pendingQuestion = isAnsweringFollowUp
          ? [...session.messages]
              .reverse()
              .find((m) => m.message_kind === "followup_question" && !answeredQuestionIds.has(m.id)) ??
            [...session.messages].reverse().find((m) => m.message_kind === "followup_question")
          : undefined;
        const targetFollowUpQuestionId = pendingQuestion?.id;
        const accepted = isAnsweringFollowUp
          ? await createCaseChatMessage(
              caseId,
              content,
              submission.key,
              selection.signal,
              "followup_answer",
              targetFollowUpQuestionId,
            )
          : await createCaseChatMessage(
              caseId,
              content,
              submission.key,
              selection.signal,
            );
        if (!session.isCurrentSelection(selection)) return;
        session.acceptSubmission(selection, submission.key, accepted);

        if (currentCase) {
          upsertCase({
            ...currentCase,
            status: "processing",
            active_run_id: accepted.run.id,
            latest_run_id: accepted.run.id,
            processing_status: "queued",
          });
        }

        const completed = await session.monitorCaseRun(selection, caseId, accepted.run.id);
        if (!isAnsweringFollowUp && completed && session.isCurrentSelection(selection) &&
          !hasCompletedAssistantOutput(completed, accepted.message.ordinal)) {
          session.reportError("The completed run did not persist an assistant response. Retry the saved answer.");
        }
      } catch (error) {
        if (initialSelection && (isChatRequestCanceled(initialSelection.signal, error) || !session.isCurrentSelection(initialSelection))) return;
        session.failSubmission(submissionKind, statusBeforeSubmit, getApiErrorMessage(
          error,
          submissionKind === "followup"
            ? "The clarification answer could not be sent. Retry sending the answer."
            : "The message could not be submitted.",
        ));
      } finally {
        submissionsRef.current.delete(initialSelection);
      }
    })();
  }, [caseId, cases, session, upsertCase]);

  return { submitContent };
}
