"use client";

import { skipToken, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  getApiErrorMessage,
  getCaseChat,
  getCaseRun,
  type CaseChatMessageAccepted,
  type CaseChatDetail,
  type CaseChatRead,
} from "@/lib/api";
import { caseQueryKeys } from "@/hooks/useCaseQueries";
import { isChatRequestCanceled, pollCaseRunUntilSettled } from "../runs/chat-polling";
import { determineCaseChatPhase, useChatDraft } from "./use-chat-draft";
import { activeCaseChatFollowUp } from "@/lib/chat-followup";

export interface CaseChatSelection {
  readonly caseId: string;
  readonly signal: AbortSignal;
}

async function readCaseChatDetail(caseId: string, signal: AbortSignal): Promise<CaseChatDetail> {
  const response = await getCaseChat(caseId, signal);
  return { ...response, messages: [...response.messages].sort((left, right) => left.ordinal - right.ordinal) };
}

export function useCaseChatSelection({
  cacheUpsertCaseChat,
}: {
  cacheUpsertCaseChat: (chat: CaseChatRead) => void;
}) {
  const queryClient = useQueryClient();
  const [activeCaseChatId, setActiveCaseChatId] = useState<string | null>(null);
  const selectionRef = useRef<CaseChatSelection | null>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const inactiveCaseChatIds = useRef(new Set<string>());
  const draft = useChatDraft();
  const {
    reconcile, selectDraft, clearDraft, forgetCaseChat, failSelection,
    acceptSubmission: acceptDraftSubmission,
  } = draft;

  const chatQuery = useQuery<CaseChatDetail>({
    queryKey: caseQueryKeys.chat(activeCaseChatId ?? "none"),
    queryFn: activeCaseChatId === null
      ? skipToken
      : ({ signal }) => readCaseChatDetail(activeCaseChatId, signal),
    enabled: false,
    retry: false,
  });
  const detail = chatQuery.data;
  const getSelection = useCallback(() => selectionRef.current, []);
  const getActiveCaseChatId = useCallback(() => selectionRef.current?.caseId ?? null, []);
  const isCurrentSelection = useCallback((selection: CaseChatSelection) =>
    selectionRef.current === selection && !selection.signal.aborted &&
    !inactiveCaseChatIds.current.has(selection.caseId), []);

  const upsertCaseChat = useCallback((chat: CaseChatRead) => {
    if (!inactiveCaseChatIds.current.has(chat.case_id)) cacheUpsertCaseChat(chat);
  }, [cacheUpsertCaseChat]);

  const readChat = useCallback((selection: CaseChatSelection) => queryClient.fetchQuery({
    queryKey: caseQueryKeys.chat(selection.caseId),
    queryFn: ({ signal }) => readCaseChatDetail(selection.caseId, signal),
    staleTime: 0,
    retry: false,
  }), [queryClient]);

  const applyCaseChat = useCallback((chat: CaseChatDetail, failureMessage?: string) => {
    queryClient.setQueryData(caseQueryKeys.chat(chat.case_id), chat);
    upsertCaseChat(chat);
    reconcile(chat, failureMessage);
  }, [queryClient, reconcile, upsertCaseChat]);

  const monitorCaseRun = useCallback((
    selection: CaseChatSelection,
    caseId: string,
    runId: string,
  ) => pollCaseRunUntilSettled({
    runId,
    signal: selection.signal,
    isCurrent: () => isCurrentSelection(selection),
    readRun: () => getCaseRun(caseId, runId, selection.signal),
    readCaseChat: () => readChat(selection),
    applyCaseChat: (chat, failureMessage) => {
      applyCaseChat(chat, failureMessage);
      void queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId) });
      void queryClient.invalidateQueries({ queryKey: caseQueryKeys.analysis(caseId) });
      void queryClient.invalidateQueries({ queryKey: caseQueryKeys.evidence(caseId) });
      void queryClient.invalidateQueries({ queryKey: caseQueryKeys.followups(caseId) });
      void queryClient.refetchQueries({
        queryKey: caseQueryKeys.chat(selection.caseId),
        exact: true,
        type: "all",
      });
    },
  }), [applyCaseChat, isCurrentSelection, queryClient, readChat]);

  const cancelSelection = useCallback(() => {
    const previous = selectionRef.current;
    controllerRef.current?.abort();
    controllerRef.current = null;
    selectionRef.current = null;
    if (previous) {
      void queryClient.cancelQueries({ queryKey: caseQueryKeys.chat(previous.caseId), exact: true });
    }
  }, [queryClient]);

  const refreshCaseChat = useCallback(async (caseId?: string) => {
    const targetId = caseId ?? activeCaseChatId;
    if (!targetId || inactiveCaseChatIds.current.has(targetId)) return;
    const controller = new AbortController();
    const selection = { caseId: targetId, signal: controller.signal };
    try {
      const chat = await readChat(selection);
      if (inactiveCaseChatIds.current.has(targetId)) return;
      queryClient.setQueryData(caseQueryKeys.chat(targetId), chat);
      applyCaseChat(chat);
    } catch (error) {
      if (!isChatRequestCanceled(selection.signal, error)) {
        failSelection(getApiErrorMessage(error, "The Case Chat could not be loaded."));
      }
    }
  }, [activeCaseChatId, applyCaseChat, failSelection, queryClient, readChat]);

  const selectCaseChat = useCallback(async (caseId: string) => {
    if (inactiveCaseChatIds.current.has(caseId)) return;
    if (selectionRef.current?.caseId === caseId && !selectionRef.current.signal.aborted) return;
    cancelSelection();
    const controller = new AbortController();
    const selection = { caseId, signal: controller.signal };
    controllerRef.current = controller;
    selectionRef.current = selection;
    setActiveCaseChatId(caseId);
    selectDraft(caseId);
    try {
      const chat = await readChat(selection);
      if (!isCurrentSelection(selection)) return;
      applyCaseChat(chat);
    } catch (error) {
      if (isChatRequestCanceled(selection.signal, error) || !isCurrentSelection(selection)) return;
      failSelection(getApiErrorMessage(error, "The Case Chat could not be loaded."));
    }
  }, [applyCaseChat, cancelSelection, failSelection, isCurrentSelection, readChat, selectDraft]);

  const acceptSubmission = useCallback((
    selection: CaseChatSelection,
    key: string,
    accepted: CaseChatMessageAccepted,
  ) => {
    if (!isCurrentSelection(selection)) return;
    acceptDraftSubmission(key, accepted.message.ordinal);
    queryClient.setQueryData<CaseChatDetail>(caseQueryKeys.chat(selection.caseId), (current) => {
      if (!current) throw new Error("The selected Case Chat must be loaded before accepting a submission.");
      const messages = current.messages.some((message) => message.id === accepted.message.id)
        ? current.messages
        : [...current.messages, accepted.message].sort((left, right) => left.ordinal - right.ordinal);
      return { ...current, status: "processing", messages };
    });
    const current = queryClient.getQueryData<CaseChatDetail>(caseQueryKeys.chat(selection.caseId));
    if (current) upsertCaseChat(current);
  }, [acceptDraftSubmission, isCurrentSelection, queryClient, upsertCaseChat]);

  const clearSelection = useCallback(() => {
    cancelSelection();
    setActiveCaseChatId(null);
    clearDraft();
  }, [cancelSelection, clearDraft]);

  const suspendCaseChat = useCallback((caseId: string) => {
    const wasActive = selectionRef.current?.caseId === caseId;
    inactiveCaseChatIds.current.add(caseId);
    if (wasActive) cancelSelection();
    return wasActive;
  }, [cancelSelection]);

  const restoreCaseChat = useCallback((caseId: string) => {
    inactiveCaseChatIds.current.delete(caseId);
  }, []);

  const removeCaseChat = useCallback((caseId: string) => {
    forgetCaseChat(caseId);
    queryClient.removeQueries({ queryKey: caseQueryKeys.chat(caseId), exact: true });
  }, [forgetCaseChat, queryClient]);

  const persistedFollowUp = detail
    ? activeCaseChatFollowUp(detail.messages, detail.status)
    : null;

  useEffect(() => cancelSelection, [cancelSelection]);

  return {
    activeCaseChatId,
    messages: detail?.messages ?? [],
    chatStatus: draft.state.activity ? draft.state.activity.chatStatus : detail?.status ?? null,
    phase: draft.state.activity?.phase ?? determineCaseChatPhase(detail),
    input: draft.state.input,
    pendingFollowUp: draft.state.pendingFollowUp ?? (
      detail && persistedFollowUp
        ? { caseId: detail.case_id, followUp: persistedFollowUp }
        : null
    ),
    queryError: draft.state.queryError,
    changeInput: draft.changeInput,
    reportError: draft.reportError,
    getPendingSubmission: draft.getPendingSubmission,
    beginSubmission: draft.beginSubmission,
    failSubmission: draft.failSubmission,
    getSelection,
    getActiveCaseChatId,
    isCurrentSelection,
    selectCaseChat,
    refreshCaseChat,
    monitorCaseRun,
    acceptSubmission,
    upsertCaseChat,
    clearSelection,
    suspendCaseChat,
    restoreCaseChat,
    removeCaseChat,
  };
}

export type CaseChatSession = ReturnType<typeof useCaseChatSelection>;
