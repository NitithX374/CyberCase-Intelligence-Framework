"use client";

import { useCallback, useRef, type FormEvent } from "react";
import {
  createCaseChatMessage,
  getApiErrorMessage,
  type CaseFollowUpAnswer,
  type CaseRead,
} from "@/lib/api";
import {
  hasCompletedAssistantOutput,
  type ChatFollowUpAnswer,
} from "@/lib/chat-followup";
import { isChatRequestCanceled } from "./chat-polling";
import type { PendingChatSubmission } from "../workspace/use-chat-draft";
import type { CaseChatSelection, CaseChatSession } from "../workspace/use-case-chat-selection";

interface UseCaseChatSubmissionOptions {
  session: CaseChatSession;
  cases: CaseRead[];
  upsertCase: (caseRecord: CaseRead) => void;
  caseId: string | null;
}

export function useCaseChatSubmission({
  session,
  cases,
  upsertCase,
  caseId,
}: UseCaseChatSubmissionOptions) {
  const submissionsRef = useRef(new Set<CaseChatSelection | null>());

  const submitFollowUp = useCallback((answer: ChatFollowUpAnswer) => {
    if (caseId === null) {
      session.reportError("Open a Case before sending clarification answers.");
      return;
    }
    const followUp = session.pendingFollowUp?.followUp;
    if (!followUp || answer.gapId !== followUp.gap.gapId) {
      session.reportError("Select the current clarification gap before sending an answer.");
      return;
    }
    const selection = session.getSelection();
    if (!selection || session.phase === "querying" || session.phase === "analyzing") return;
    if (submissionsRef.current.has(selection)) return;

    const content = formatFollowUpAnswer(answer);
    const currentCase = cases.find((caseRecord) => caseRecord.id === caseId);
    const saved = session.getPendingSubmission();
    const samePending = saved?.caseId === caseId &&
      saved.kind === "followup" &&
      saved.content === content &&
      JSON.stringify(saved.followUpAnswer) === JSON.stringify(answer);
    const submission: PendingChatSubmission = samePending && saved ? saved : {
      caseId,
      content,
      key: window.crypto.randomUUID(),
      kind: "followup",
      lastKnownMessageOrdinal: session.messages.reduce(
        (ordinal, message) => Math.max(ordinal, message.ordinal),
        0,
      ),
      followUpAnswer: answer,
      followUpQuestionId: followUp.questionMessageId,
    };
    submissionsRef.current.add(selection);

    void (async () => {
      try {
        session.beginSubmission(submission, followUp);
        const accepted = await createCaseChatMessage(
          caseId,
          content,
          submission.key,
          selection.signal,
          "followup_answer",
          followUp.questionMessageId,
          toApiFollowUpAnswer(answer),
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
        await session.monitorCaseRun(selection, caseId, accepted.run.id);
      } catch (error) {
        if (isChatRequestCanceled(selection.signal, error) || !session.isCurrentSelection(selection)) return;
        session.failSubmission("followup", "awaiting_followup", getApiErrorMessage(
          error,
          "The clarification answer could not be sent. Retry it or continue with Ask.",
        ));
      } finally {
        submissionsRef.current.delete(selection);
      }
    })();
  }, [caseId, cases, session, upsertCase]);

  const submitContent = useCallback((rawContent: string, kind: PendingChatSubmission["kind"] = "message") => {
    if (kind !== "message") return;
    if (caseId === null) {
      session.reportError("Open a Case before sending a message.");
      return;
    }
    if (session.phase === "querying" || session.phase === "analyzing") return;
    const content = rawContent.trim();
    if (!content) return;
    const selection = session.getSelection();
    if (!selection || submissionsRef.current.has(selection)) return;
    const currentCase = cases.find((caseRecord) => caseRecord.id === caseId);
    const saved = session.getPendingSubmission();
    const submission: PendingChatSubmission = saved?.caseId === caseId &&
      saved.content === content && saved.kind === "message" ? saved : {
        caseId,
        content,
        key: window.crypto.randomUUID(),
        kind: "message",
        lastKnownMessageOrdinal: session.messages.reduce(
          (ordinal, message) => Math.max(ordinal, message.ordinal),
          0,
        ),
      };
    const statusBeforeSubmit = session.chatStatus;
    submissionsRef.current.add(selection);

    void (async () => {
      try {
        session.beginSubmission(submission);
        const accepted = await createCaseChatMessage(
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
        if (
          completed &&
          session.isCurrentSelection(selection) &&
          !hasCompletedAssistantOutput(completed, accepted.message.ordinal)
        ) {
          session.reportError("The completed run did not persist an assistant response. Retry the saved message.");
        }
      } catch (error) {
        if (isChatRequestCanceled(selection.signal, error) || !session.isCurrentSelection(selection)) return;
        session.failSubmission("message", statusBeforeSubmit, getApiErrorMessage(
          error,
          "The message could not be submitted.",
        ));
      } finally {
        submissionsRef.current.delete(selection);
      }
    })();
  }, [caseId, cases, session, upsertCase]);

  const submitMessage = useCallback((event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    submitContent(session.input);
  }, [session.input, submitContent]);

  const clearQueryError = useCallback(() => session.reportError(null), [session]);

  const retryQuery = useCallback(() => {
    const pending = session.getPendingSubmission();
    if (!pending || pending.caseId !== session.getActiveCaseChatId()) return;
    session.reportError(null);
    if (pending.kind === "followup" && pending.followUpAnswer) {
      submitFollowUp(pending.followUpAnswer);
      return;
    }
    submitContent(pending.content);
  }, [session, submitContent, submitFollowUp]);

  return {
    submitContent,
    submitFollowUp,
    clearQueryError,
    retryQuery,
    submitMessage,
  };
}

function toApiFollowUpAnswer(answer: ChatFollowUpAnswer): CaseFollowUpAnswer {
  return {
    gap_id: answer.gapId,
    answer: answer.answer,
    disposition: answer.disposition,
  };
}

function formatFollowUpAnswer(answer: ChatFollowUpAnswer): string {
  return answer.disposition === "answered" ? answer.answer ?? "" : answer.disposition;
}
