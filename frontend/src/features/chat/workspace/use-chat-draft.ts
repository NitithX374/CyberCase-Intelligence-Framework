"use client";

import { accountStorageKey, readAccountValue, writeAccountValue } from "@/lib/account-storage";
import { useCallback, useRef, useState } from "react";
import type { CaseChatDetail, CaseChatStatus } from "@/lib/api";
import type { RunPhase } from "@/components/common/types";
import {
  hasCompletedAssistantOutput,
  persistedRequestOrdinal,
  type ActiveChatFollowUp,
} from "@/lib/chat-followup";

export interface PendingChatSubmission {
  caseId: string;
  content: string;
  key: string;
  kind: "message" | "followup";
  lastKnownMessageOrdinal: number;
  requestOrdinal?: number;
}

interface ChatDraftState {
  input: string;
  pendingFollowUp: { caseId: string; followUp: ActiveChatFollowUp } | null;
  queryError: string | null;
  activity: { phase: RunPhase; chatStatus: CaseChatStatus | null } | null;
}

const emptyDraft: ChatDraftState = {
  input: "", pendingFollowUp: null,
  queryError: null, activity: null,
};

export function determineCaseChatPhase(detail: CaseChatDetail | undefined): RunPhase {
  if (!detail) return "idle";
  if (detail.status === "processing") return "querying";
  if (detail.status === "awaiting_followup") return "awaiting_followup";
  if (detail.status === "failed") return "error";
  return detail.messages.length > 0 ? "ready" : "idle";
}

export const phaseForCaseChat = determineCaseChatPhase;

export function useChatDraft() {
  const [state, setState] = useState(() => ({ ...emptyDraft, input: readAccountValue("draft:new") ?? "" }));
  const draftCaseRef = useRef("new");
  const pendingRef = useRef<PendingChatSubmission | null>(null);
  const getPendingSubmission = useCallback(() => pendingRef.current, []);
  const changeInput = useCallback((input: string) => {
    writeAccountValue(`draft:${draftCaseRef.current}`, input);
    setState((current) => ({ ...current, input }));
  }, []);
  const reportError = useCallback((queryError: string | null) => {
    setState((current) => ({ ...current, queryError }));
  }, []);
  const selectDraft = useCallback((caseId: string) => {
    const previousCaseId = draftCaseRef.current;
    draftCaseRef.current = caseId;
    if (pendingRef.current?.caseId !== caseId) pendingRef.current = readPendingSubmission(caseId);
    const pending = pendingRef.current;
    setState((current) => {
      const persistedDraft = readAccountValue(`draft:${caseId}`) ?? "";
      const isUnsavedNewDraft = previousCaseId === "new" && Boolean(current.input) && !persistedDraft;
      const input = pending?.caseId === caseId && pending.kind === "followup"
        ? pending.content
        : isUnsavedNewDraft
          ? current.input
          : persistedDraft;
      if (isUnsavedNewDraft) {
        writeAccountValue(`draft:${caseId}`, current.input);
      }
      return {
        ...current,
        input,
        pendingFollowUp: current.pendingFollowUp?.caseId === caseId ? current.pendingFollowUp : null,
        queryError: pending?.caseId === caseId ? current.queryError : null,
        activity: pending ? { phase: "querying", chatStatus: "processing" } : null,
      };
    });
  }, []);
  const beginSubmission = useCallback((pending: PendingChatSubmission, followUp?: ActiveChatFollowUp) => {
    pendingRef.current = pending;
    persistPendingSubmission(pending);
    setState((current) => ({
      ...current, queryError: null,
      activity: { phase: "querying", chatStatus: "processing" },
      pendingFollowUp: followUp ? { caseId: pending.caseId, followUp } : current.pendingFollowUp,
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
    statusBeforeSubmit: CaseChatStatus | null,
    queryError: string,
  ) => {
    setState((current) => ({
      ...current, queryError,
      activity: kind === "followup"
        ? { phase: "awaiting_followup", chatStatus: "awaiting_followup" }
        : { phase: "error", chatStatus: statusBeforeSubmit },
    }));
  }, []);
  const failSelection = useCallback((queryError: string) => {
    setState((current) => ({
      ...current, queryError, activity: { phase: "error", chatStatus: null },
    }));
  }, []);
  const reconcile = useCallback((detail: CaseChatDetail, failureMessage?: string) => {
    if (!pendingRef.current) pendingRef.current = readPendingSubmission(detail.case_id);
    const pending = pendingRef.current;
    const requestOrdinal = pending?.caseId === detail.case_id
      ? pending.requestOrdinal ?? persistedRequestOrdinal(detail, pending.lastKnownMessageOrdinal, pending.content)
      : undefined;
    if (pending?.caseId === detail.case_id && requestOrdinal !== undefined) {
      pendingRef.current = { ...pending, requestOrdinal };
      persistPendingSubmission(pendingRef.current);
    }
    const isFollowup = pending?.kind === "followup";
    const completed = pending?.caseId === detail.case_id && requestOrdinal !== undefined &&
      (isFollowup
        ? (detail.status === "idle" || detail.status === "answered" || detail.status === "awaiting_followup")
        : hasCompletedAssistantOutput(detail, requestOrdinal));
    if (completed) {
      pendingRef.current = null;
      removePendingSubmission(detail.case_id);
      writeAccountValue(`draft:${detail.case_id}`, "");
    }
    setState((current) => ({
      ...current, activity: null,
      queryError: failureMessage || (detail.status === "failed"
        ? "Background processing failed. Retry the saved message."
        : pending?.caseId !== detail.case_id || requestOrdinal !== undefined ? null : current.queryError),
      ...(completed ? { input: "", pendingFollowUp: null } : {}),
    }));
  }, []);
  const clearDraft = useCallback(() => {
    draftCaseRef.current = "new";
    setState({ ...emptyDraft, input: readAccountValue("draft:new") ?? "" });
  }, []);
  const forgetCaseChat = useCallback((caseId: string) => {
    if (pendingRef.current?.caseId === caseId) pendingRef.current = null;
    removePendingSubmission(caseId);
    setState((current) => current.pendingFollowUp?.caseId === caseId
      ? { ...current, pendingFollowUp: null } : current);
  }, []);

  return {
    state, getPendingSubmission, changeInput, reportError,
    selectDraft, beginSubmission, acceptSubmission, failSubmission, failSelection,
    reconcile, clearDraft, forgetCaseChat,
  };
}

function pendingStorageKey(caseId: string): string {
  return `pending-case-chat:${caseId}`;
}

function readPendingSubmission(caseId: string): PendingChatSubmission | null {
  const saved = readAccountValue(pendingStorageKey(caseId));
  return saved === null ? null : JSON.parse(saved) as PendingChatSubmission;
}

function persistPendingSubmission(pending: PendingChatSubmission): void {
  writeAccountValue(pendingStorageKey(pending.caseId), JSON.stringify(pending));
}

function removePendingSubmission(caseId: string): void {
  if (typeof window !== "undefined") localStorage.removeItem(accountStorageKey(pendingStorageKey(caseId)));
}
