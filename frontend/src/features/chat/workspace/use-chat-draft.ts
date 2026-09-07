"use client";

import { useCallback, useRef, useState } from "react";
import type { ChatMessageAction, ChatThreadDetail, ThreadStatus } from "@/lib/api";
import type { RunPhase } from "@/components/common/types";
import {
  hasCompletedAssistantOutput,
  persistedRequestOrdinal,
  type ActiveChatFollowUp,
} from "@/lib/chat-followup";
import type { PendingChatSubmission } from "./chat-workspace-types";
import { restoreInterruptedSubmission } from "./chat-retry-request";

interface ChatDraftState {
  input: string;
  postAnswerAction: ChatMessageAction | null;
  pendingFollowUp: { threadId: string; followUp: ActiveChatFollowUp } | null;
  queryError: string | null;
  activity: { phase: RunPhase; threadStatus: ThreadStatus | null } | null;
}

const emptyDraft: ChatDraftState = {
  input: "", postAnswerAction: null, pendingFollowUp: null,
  queryError: null, activity: null,
};

export function phaseForThread(detail: ChatThreadDetail | undefined): RunPhase {
  if (!detail) return "idle";
  if (detail.status === "processing") return "querying";
  if (detail.status === "awaiting_followup") return "awaiting_followup";
  if (detail.status === "failed") return "error";
  return detail.messages.length > 0 ? "ready" : "idle";
}

export function useChatDraft() {
  const [state, setState] = useState(emptyDraft);
  const pendingRef = useRef<PendingChatSubmission | null>(null);
  const getPendingSubmission = useCallback(() => pendingRef.current, []);
  const changeInput = useCallback((input: string) => {
    setState((current) => ({ ...current, input }));
  }, []);
  const changePostAnswerAction = useCallback((postAnswerAction: ChatMessageAction | null) => {
    setState((current) => ({ ...current, postAnswerAction }));
  }, []);
  const reportError = useCallback((queryError: string | null) => {
    setState((current) => ({ ...current, queryError }));
  }, []);
  const selectDraft = useCallback((threadId: string) => {
    const pending = pendingRef.current;
    setState((current) => ({
      ...current,
      input: pending?.threadId === threadId && pending.kind === "followup" ? pending.content : "",
      postAnswerAction: pending?.threadId === threadId ? pending.action ?? null : null,
      pendingFollowUp: current.pendingFollowUp?.threadId === threadId ? current.pendingFollowUp : null,
      queryError: pending?.threadId === threadId ? current.queryError : null,
      activity: { phase: "querying", threadStatus: null },
    }));
  }, []);
  const beginSubmission = useCallback((pending: PendingChatSubmission, followUp?: ActiveChatFollowUp) => {
    pendingRef.current = pending;
    setState((current) => ({
      ...current, queryError: null,
      activity: { phase: "querying", threadStatus: "processing" },
      pendingFollowUp: followUp ? { threadId: pending.threadId, followUp } : current.pendingFollowUp,
    }));
  }, []);
  const acceptSubmission = useCallback((key: string, ordinal: number) => {
    const pending = pendingRef.current;
    if (pending?.key === key) pendingRef.current = { ...pending, requestOrdinal: ordinal };
  }, []);
  const failSubmission = useCallback((
    kind: PendingChatSubmission["kind"],
    statusBeforeSubmit: ThreadStatus | null,
    queryError: string,
  ) => {
    setState((current) => ({
      ...current, queryError,
      activity: kind === "followup"
        ? { phase: "awaiting_followup", threadStatus: "awaiting_followup" }
        : { phase: "error", threadStatus: statusBeforeSubmit },
    }));
  }, []);
  const failSelection = useCallback((queryError: string) => {
    setState((current) => ({
      ...current, queryError, activity: { phase: "error", threadStatus: null },
    }));
  }, []);
  const reconcile = useCallback((detail: ChatThreadDetail, failureMessage?: string) => {
    const restored = restoreInterruptedSubmission(detail);
    if (restored) pendingRef.current = restored;
    const pending = pendingRef.current;
    const requestOrdinal = pending?.threadId === detail.id
      ? pending.requestOrdinal ?? persistedRequestOrdinal(detail, pending.lastKnownMessageOrdinal, pending.content)
      : undefined;
    if (pending?.threadId === detail.id && requestOrdinal !== undefined) {
      pendingRef.current = { ...pending, requestOrdinal };
    }
    const completed = pending?.threadId === detail.id && requestOrdinal !== undefined &&
      hasCompletedAssistantOutput(detail, requestOrdinal);
    if (completed) pendingRef.current = null;
    setState((current) => ({
      ...current, activity: null,
      ...(restored ? { postAnswerAction: restored.action ?? null } : {}),
      queryError: failureMessage || (detail.status === "failed"
        ? "Background processing failed. Retry the saved message."
        : pending?.threadId !== detail.id || requestOrdinal !== undefined ? null : current.queryError),
      ...(completed ? { input: "", pendingFollowUp: null, postAnswerAction: null } : {}),
    }));
  }, []);
  const clearDraft = useCallback(() => {
    setState(emptyDraft);
  }, []);
  const forgetThread = useCallback((threadId: string) => {
    if (pendingRef.current?.threadId === threadId) pendingRef.current = null;
    setState((current) => current.pendingFollowUp?.threadId === threadId
      ? { ...current, pendingFollowUp: null } : current);
  }, []);

  return {
    state, getPendingSubmission, changeInput, changePostAnswerAction, reportError,
    selectDraft, beginSubmission, acceptSubmission, failSubmission, failSelection,
    reconcile, clearDraft, forgetThread,
  };
}
