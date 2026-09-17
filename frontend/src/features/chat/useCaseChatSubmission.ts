"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, type FormEvent } from "react";
import {
  createCaseChatMessage,
  getApiErrorMessage,
  type CaseChatDetail,
  type CaseChatStatus,
  type CaseFollowUpAnswer,
  type CaseRead,
  type ChatMessageRead,
} from "@/lib/api";
import { caseQueryKeys } from "@/hooks/useCaseQueries";
import type { RunPhase } from "@/components/common/types";
import {
  type ActiveChatFollowUp,
  type ChatFollowUpAnswer,
} from "@/lib/chat-followup";
import type { ChatDraftSession, PendingChatSubmission } from "./useChatDraft";

export interface UseCaseChatSubmissionOptions {
  caseId: string | null;
  draft: ChatDraftSession;
  messages: ChatMessageRead[];
  chatStatus: CaseChatStatus | null;
  phase: RunPhase;
  pendingFollowUp: { caseId: string; followUp: ActiveChatFollowUp } | null;
  currentCase?: CaseRead | null;
  upsertCase?: (caseRecord: CaseRead) => void;
}

function isRequestCanceled(signal: AbortSignal, error: unknown): boolean {
  return signal.aborted || (
    typeof error === "object" && error !== null &&
    "code" in error && error.code === "ERR_CANCELED"
  );
}

export function useCaseChatSubmission({
  caseId,
  draft,
  messages,
  chatStatus,
  phase,
  pendingFollowUp,
  currentCase,
  upsertCase,
}: UseCaseChatSubmissionOptions) {
  const queryClient = useQueryClient();
  const activeCaseIdRef = useRef<string | null>(caseId);
  const submissionsRef = useRef(new Set<string>());

  useEffect(() => {
    activeCaseIdRef.current = caseId;
  }, [caseId]);

  const submitFollowUp = useCallback((answer: ChatFollowUpAnswer) => {
    if (caseId === null) {
      draft.reportError("Open a Case before sending clarification answers.");
      return;
    }
    const activeFollowUp = pendingFollowUp?.followUp;
    if (!activeFollowUp || answer.gapId !== activeFollowUp.gap.gapId) {
      draft.reportError("Select the current clarification gap before sending an answer.");
      return;
    }
    if (phase === "querying" || phase === "analyzing") return;
    if (submissionsRef.current.has(caseId)) return;

    const targetCaseId = caseId;
    const content = formatFollowUpAnswer(answer);
    const saved = draft.getPendingSubmission();
    const samePending = saved?.caseId === targetCaseId &&
      saved.kind === "followup" &&
      saved.content === content &&
      JSON.stringify(saved.followUpAnswer) === JSON.stringify(answer);

    const submission: PendingChatSubmission = samePending && saved ? saved : {
      caseId: targetCaseId,
      content,
      key: window.crypto.randomUUID(),
      kind: "followup",
      lastKnownMessageOrdinal: messages.reduce(
        (ordinal, message) => Math.max(ordinal, message.ordinal),
        0,
      ),
      followUpAnswer: answer,
      followUpQuestionId: activeFollowUp.questionMessageId,
    };

    submissionsRef.current.add(targetCaseId);
    const controller = new AbortController();

    void (async () => {
      try {
        draft.beginSubmission(submission, activeFollowUp);
        const accepted = await createCaseChatMessage(
          targetCaseId,
          content,
          submission.key,
          controller.signal,
          "followup_answer",
          activeFollowUp.questionMessageId,
          toApiFollowUpAnswer(answer),
        );

        const nextStatus: CaseChatStatus = "answered";

        // RACE GUARD: If active case changed during in-flight POST
        if (activeCaseIdRef.current !== targetCaseId) {
          queryClient.setQueryData<CaseChatDetail>(caseQueryKeys.chat(targetCaseId), (current) => {
            if (!current) return current;
            const updated = current.messages.some((m) => m.id === accepted.message.id)
              ? current.messages
              : [...current.messages, accepted.message].sort((a, b) => a.ordinal - b.ordinal);
            return { ...current, status: nextStatus, messages: updated };
          });
          return;
        }

        draft.acceptSubmission(submission.key, accepted.message.ordinal);
        queryClient.setQueryData<CaseChatDetail>(caseQueryKeys.chat(targetCaseId), (current) => {
          const base = current ?? { case_id: targetCaseId, status: nextStatus, messages: [] };
          const updated = base.messages.some((m) => m.id === accepted.message.id)
            ? base.messages
            : [...base.messages, accepted.message].sort((a, b) => a.ordinal - b.ordinal);
          return { ...base, status: nextStatus, messages: updated };
        });

        if (accepted.run) {
          // Seed the run into the cache so useCaseRunPolling picks it up immediately
          queryClient.setQueryData(
            caseQueryKeys.run(targetCaseId, accepted.run.id),
            accepted.run,
          );
          if (currentCase && upsertCase) {
            upsertCase({
              ...currentCase,
              status: "processing",
              active_run_id: accepted.run.id,
              latest_run_id: accepted.run.id,
              processing_status: "queued",
            });
          }
          // useCaseRunPolling in the layout handles polling + settlement invalidation
        } else {
          draft.completeSubmissionWithoutRun(targetCaseId);
          void queryClient.invalidateQueries({ queryKey: caseQueryKeys.chat(targetCaseId) });
          void queryClient.invalidateQueries({ queryKey: caseQueryKeys.followups(targetCaseId) });
        }
      } catch (error) {
        if (isRequestCanceled(controller.signal, error) || activeCaseIdRef.current !== targetCaseId) return;
        draft.failSubmission("followup", "awaiting_followup", getApiErrorMessage(
          error,
          "The clarification answer could not be sent. Retry it or continue with Ask.",
        ));
      } finally {
        submissionsRef.current.delete(targetCaseId);
      }
    })();
  }, [caseId, currentCase, draft, messages, pendingFollowUp, phase, queryClient, upsertCase]);

  const submitContent = useCallback((rawContent: string, kind: PendingChatSubmission["kind"] = "message") => {
    if (kind !== "message") return;
    if (caseId === null) {
      draft.reportError("Open a Case before sending a message.");
      return;
    }
    if (phase === "querying" || phase === "analyzing") return;
    const content = rawContent.trim();
    if (!content) return;
    if (submissionsRef.current.has(caseId)) return;

    const targetCaseId = caseId;
    const saved = draft.getPendingSubmission();
    const samePending = saved?.caseId === targetCaseId &&
      saved.content === content &&
      saved.kind === "message";

    const submission: PendingChatSubmission = samePending && saved ? saved : {
      caseId: targetCaseId,
      content,
      key: window.crypto.randomUUID(),
      kind: "message",
      lastKnownMessageOrdinal: messages.reduce(
        (ordinal, message) => Math.max(ordinal, message.ordinal),
        0,
      ),
    };

    const statusBeforeSubmit = chatStatus;
    submissionsRef.current.add(targetCaseId);
    const controller = new AbortController();

    void (async () => {
      try {
        draft.beginSubmission(submission);
        const result = await createCaseChatMessage(
          targetCaseId,
          content,
          submission.key,
          controller.signal,
        );

        const newMessages = [
          result.message,
          ...(result.assistant_message ? [result.assistant_message] : []),
        ];

        // RACE GUARD: If active case changed during in-flight POST
        if (activeCaseIdRef.current !== targetCaseId) {
          queryClient.setQueryData<CaseChatDetail>(caseQueryKeys.chat(targetCaseId), (current) => {
            if (!current) return current;
            const existingIds = new Set(current.messages.map((m) => m.id));
            const toAdd = newMessages.filter((m) => !existingIds.has(m.id));
            const updated = [...current.messages, ...toAdd].sort((a, b) => a.ordinal - b.ordinal);
            return { ...current, status: "answered", messages: updated };
          });
          return;
        }

        queryClient.setQueryData<CaseChatDetail>(caseQueryKeys.chat(targetCaseId), (current) => {
          const base = current ?? { case_id: targetCaseId, status: "answered", messages: [] };
          const existingIds = new Set(base.messages.map((m) => m.id));
          const toAdd = newMessages.filter((m) => !existingIds.has(m.id));
          const updated = [...base.messages, ...toAdd].sort((a, b) => a.ordinal - b.ordinal);
          return { ...base, status: "answered", messages: updated };
        });

        draft.completeSubmission(targetCaseId);
        void queryClient.invalidateQueries({ queryKey: caseQueryKeys.chat(targetCaseId) });
      } catch (error) {
        if (isRequestCanceled(controller.signal, error) || activeCaseIdRef.current !== targetCaseId) return;
        draft.failSubmission("message", statusBeforeSubmit, getApiErrorMessage(
          error,
          "The message could not be submitted.",
        ));
      } finally {
        submissionsRef.current.delete(targetCaseId);
      }
    })();
  }, [caseId, chatStatus, draft, messages, phase, queryClient]);

  const submitMessage = useCallback((event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    submitContent(draft.state.input);
  }, [draft.state.input, submitContent]);

  const clearQueryError = useCallback(() => draft.reportError(null), [draft]);

  const retryQuery = useCallback(() => {
    const pending = draft.getPendingSubmission();
    if (!pending || pending.caseId !== caseId) return;
    draft.reportError(null);
    if (pending.kind === "followup" && pending.followUpAnswer) {
      submitFollowUp(pending.followUpAnswer);
      return;
    }
    submitContent(pending.content);
  }, [caseId, draft, submitContent, submitFollowUp]);

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
