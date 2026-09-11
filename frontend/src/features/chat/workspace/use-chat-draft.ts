"use client";

import { accountStorageKey, readAccountValue, writeAccountValue } from "@/lib/account-storage";
import { useCallback, useRef, useState } from "react";
import type { ChatMessageAction, ChatThreadDetail, ThreadStatus } from "@/lib/api";
import type { RunPhase } from "@/components/common/types";
import {
  hasCompletedAssistantOutput,
  persistedRequestOrdinal,
  type ActiveChatFollowUp,
} from "@/lib/chat-followup";
import type { PendingChatSubmission } from "./chat-workspace-types";

interface ChatDraftState {
  input: string;
  postAnswerAction: ChatMessageAction | null;
  pendingFollowUp: { threadId: string; followUp: ActiveChatFollowUp } | null;
  queryError: string | null;
  activity: { phase: RunPhase; threadStatus: ThreadStatus | null } | null;
}

const emptyDraft: ChatDraftState = {
  input: "", postAnswerAction: "ask", pendingFollowUp: null,
  queryError: null, activity: null,
};

export function determineThreadPhase(detail: ChatThreadDetail | undefined): RunPhase {
  if (!detail) return "idle";
  if (detail.status === "processing") return "querying";
  if (detail.status === "awaiting_followup") return "awaiting_followup";
  if (detail.status === "failed") return "error";
  return detail.messages.length > 0 ? "ready" : "idle";
}

export const phaseForThread = determineThreadPhase;

export function useChatDraft() {
  const [state, setState] = useState(() => ({ ...emptyDraft, input: readAccountValue("draft:new") ?? "" }));
  const draftThreadRef = useRef("new");
  const pendingRef = useRef<PendingChatSubmission | null>(null);
  const getPendingSubmission = useCallback(() => pendingRef.current, []);
  const changeInput = useCallback((input: string) => {
    writeAccountValue(`draft:${draftThreadRef.current}`, input);
    setState((current) => ({ ...current, input }));
  }, []);
  const changePostAnswerAction = useCallback((postAnswerAction: ChatMessageAction | null) => {
    writeAccountValue(`action:${draftThreadRef.current}`, postAnswerAction ?? "ask");
    setState((current) => ({ ...current, postAnswerAction }));
  }, []);
  const reportError = useCallback((queryError: string | null) => {
    setState((current) => ({ ...current, queryError }));
  }, []);
  const selectDraft = useCallback((threadId: string) => {
    draftThreadRef.current = threadId;
    if (pendingRef.current?.threadId !== threadId) pendingRef.current = readPendingSubmission(threadId);
    const pending = pendingRef.current;
    setState((current) => ({
      ...current,
      input: pending?.threadId === threadId && pending.kind === "followup" ? pending.content : readAccountValue(`draft:${threadId}`) ?? "",
      postAnswerAction: pending?.threadId === threadId ? pending.action ?? "ask" : readAccountValue(`action:${threadId}`) === "add_case_info" ? "add_case_info" : "ask",
      pendingFollowUp: current.pendingFollowUp?.threadId === threadId ? current.pendingFollowUp : null,
      queryError: pending?.threadId === threadId ? current.queryError : null,
      activity: { phase: "querying", threadStatus: null },
    }));
  }, []);
  const beginSubmission = useCallback((pending: PendingChatSubmission, followUp?: ActiveChatFollowUp) => {
    pendingRef.current = pending;
    persistPendingSubmission(pending);
    setState((current) => ({
      ...current, queryError: null,
      activity: { phase: "querying", threadStatus: "processing" },
      pendingFollowUp: followUp ? { threadId: pending.threadId, followUp } : current.pendingFollowUp,
    }));
  }, []);
  const acceptSubmission = useCallback((key: string, ordinal: number) => {
    const pending = pendingRef.current;
    if (pending?.key === key) {
      pendingRef.current = { ...pending, requestOrdinal: ordinal };
      persistPendingSubmission(pendingRef.current);
    }
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
    if (!pendingRef.current) pendingRef.current = readPendingSubmission(detail.id);
    const pending = pendingRef.current;
    const requestOrdinal = pending?.threadId === detail.id
      ? pending.requestOrdinal ?? persistedRequestOrdinal(detail, pending.lastKnownMessageOrdinal, pending.content)
      : undefined;
    if (pending?.threadId === detail.id && requestOrdinal !== undefined) {
      pendingRef.current = { ...pending, requestOrdinal };
      persistPendingSubmission(pendingRef.current);
    }
    const completed = pending?.threadId === detail.id && requestOrdinal !== undefined &&
      hasCompletedAssistantOutput(detail, requestOrdinal);
    if (completed) {
      pendingRef.current = null;
      removePendingSubmission(detail.id);
      writeAccountValue(`draft:${detail.id}`, "");
    }
    setState((current) => ({
      ...current, activity: null,
      queryError: failureMessage || (detail.status === "failed"
        ? "Background processing failed. Retry the saved message."
        : pending?.threadId !== detail.id || requestOrdinal !== undefined ? null : current.queryError),
      ...(completed ? { input: "", pendingFollowUp: null, postAnswerAction: "ask" } : {}),
    }));
  }, []);
  const clearDraft = useCallback(() => {
    draftThreadRef.current = "new";
    setState({ ...emptyDraft, input: readAccountValue("draft:new") ?? "" });
  }, []);
  const forgetThread = useCallback((threadId: string) => {
    if (pendingRef.current?.threadId === threadId) pendingRef.current = null;
    removePendingSubmission(threadId);
    setState((current) => current.pendingFollowUp?.threadId === threadId
      ? { ...current, pendingFollowUp: null } : current);
  }, []);

  return {
    state, getPendingSubmission, changeInput, changePostAnswerAction, reportError,
    selectDraft, beginSubmission, acceptSubmission, failSubmission, failSelection,
    reconcile, clearDraft, forgetThread,
  };
}

function pendingStorageKey(threadId: string): string {
  return `pending-case-chat:${threadId}`;
}

function readPendingSubmission(threadId: string): PendingChatSubmission | null {
  const saved = readAccountValue(pendingStorageKey(threadId));
  return saved === null ? null : JSON.parse(saved) as PendingChatSubmission;
}

function persistPendingSubmission(pending: PendingChatSubmission): void {
  writeAccountValue(pendingStorageKey(pending.threadId), JSON.stringify(pending));
}

function removePendingSubmission(threadId: string): void {
  if (typeof window !== "undefined") localStorage.removeItem(accountStorageKey(pendingStorageKey(threadId)));
}
