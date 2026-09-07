"use client";

import { skipToken, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  getApiErrorMessage, getChatThread,
  type ChatMessageAccepted, type ChatThreadDetail, type ChatThreadRead,
} from "@/lib/api";
import { chatQueryKeys } from "@/hooks/use-chat-queries";
import { isChatRequestCanceled, pollChatThreadUntilSettled } from "../runs/chat-polling";
import { phaseForThread, useChatDraft } from "./use-chat-draft";

export interface ChatSelection {
  readonly threadId: string;
  readonly signal: AbortSignal;
}

async function readChatThreadDetail(threadId: string, signal: AbortSignal) {
  const response = await getChatThread(threadId, signal);
  return { ...response, messages: [...response.messages].sort((a, b) => a.ordinal - b.ordinal) };
}

export function useChatThreadSelection({
  cacheUpsertThread,
}: { cacheUpsertThread: (thread: ChatThreadRead) => void }) {
  const queryClient = useQueryClient();
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const selectionRef = useRef<ChatSelection | null>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const deletedThreadIds = useRef(new Set<string>());
  const draft = useChatDraft();
  const {
    reconcile, selectDraft, clearDraft, forgetThread, failSelection,
    acceptSubmission: acceptDraftSubmission,
  } = draft;

  const threadQuery = useQuery<ChatThreadDetail>({
    queryKey: chatQueryKeys.detail(activeThreadId),
    queryFn: activeThreadId === null ? skipToken
      : ({ signal }) => readChatThreadDetail(activeThreadId, signal),
    enabled: false,
    retry: false,
  });
  const detail = threadQuery.data;

  const getSelection = useCallback(() => selectionRef.current, []);
  const getActiveThreadId = useCallback(() => selectionRef.current?.threadId ?? null, []);
  const isCurrentSelection = useCallback((selection: ChatSelection) =>
    selectionRef.current === selection && !selection.signal.aborted &&
    !deletedThreadIds.current.has(selection.threadId), []);

  const upsertThread = useCallback((thread: ChatThreadRead) => {
    if (!deletedThreadIds.current.has(thread.id)) cacheUpsertThread(thread);
  }, [cacheUpsertThread]);

  const readThread = useCallback((selection: ChatSelection) => queryClient.fetchQuery({
    queryKey: chatQueryKeys.detail(selection.threadId),
    queryFn: ({ signal }) => readChatThreadDetail(selection.threadId, signal),
    staleTime: 0,
    retry: false,
  }), [queryClient]);

  const applyThreadDetail = useCallback((thread: ChatThreadDetail, failureMessage?: string) => {
    upsertThread(thread);
    reconcile(thread, failureMessage);
  }, [reconcile, upsertThread]);

  const monitorThread = useCallback((selection: ChatSelection, runId?: string) =>
    pollChatThreadUntilSettled({
      threadId: selection.threadId,
      runId,
      signal: selection.signal,
      isCurrent: () => isCurrentSelection(selection),
      readThread: () => readThread(selection),
      applyThreadDetail,
    }), [applyThreadDetail, isCurrentSelection, readThread]);

  const cancelSelection = useCallback(() => {
    const previous = selectionRef.current;
    controllerRef.current?.abort();
    controllerRef.current = null;
    selectionRef.current = null;
    if (previous) {
      void queryClient.cancelQueries({ queryKey: chatQueryKeys.detail(previous.threadId), exact: true });
    }
  }, [queryClient]);

  const selectThread = useCallback(async (threadId: string) => {
    if (deletedThreadIds.current.has(threadId)) return;
    cancelSelection();
    const controller = new AbortController();
    const selection = { threadId, signal: controller.signal };
    controllerRef.current = controller;
    selectionRef.current = selection;
    setActiveThreadId(threadId);
    selectDraft(threadId);
    try {
      const thread = await readThread(selection);
      if (!isCurrentSelection(selection)) return;
      applyThreadDetail(thread);
      if (thread.status === "processing") await monitorThread(selection);
    } catch (error) {
      if (isChatRequestCanceled(selection.signal, error) || !isCurrentSelection(selection)) return;
      failSelection(getApiErrorMessage(error, "The chat could not be loaded."));
    }
  }, [applyThreadDetail, cancelSelection, failSelection, isCurrentSelection, monitorThread, readThread, selectDraft]);

  const acceptSubmission = useCallback((
    selection: ChatSelection, key: string, accepted: ChatMessageAccepted,
  ) => {
    if (!isCurrentSelection(selection)) return;
    acceptDraftSubmission(key, accepted.message.ordinal);
    queryClient.setQueryData<ChatThreadDetail>(chatQueryKeys.detail(selection.threadId), (current) => {
      if (!current) throw new Error("The selected chat must be loaded before accepting a submission.");
      const messages = current.messages.some((message) => message.id === accepted.message.id)
        ? current.messages
        : [...current.messages, accepted.message].sort((a, b) => a.ordinal - b.ordinal);
      return { ...current, status: "processing", messages };
    });
    const current = queryClient.getQueryData<ChatThreadDetail>(chatQueryKeys.detail(selection.threadId));
    if (current) upsertThread(current);
  }, [acceptDraftSubmission, isCurrentSelection, queryClient, upsertThread]);

  const clearSelection = useCallback(() => {
    cancelSelection();
    setActiveThreadId(null);
    clearDraft();
  }, [cancelSelection, clearDraft]);

  const suspendThread = useCallback((threadId: string) => {
    const wasActive = selectionRef.current?.threadId === threadId;
    deletedThreadIds.current.add(threadId);
    if (wasActive) cancelSelection();
    return wasActive;
  }, [cancelSelection]);

  const restoreThread = useCallback((threadId: string) => {
    deletedThreadIds.current.delete(threadId);
  }, []);

  const removeThread = useCallback((threadId: string) => {
    forgetThread(threadId);
    queryClient.removeQueries({ queryKey: chatQueryKeys.thread(threadId) });
  }, [forgetThread, queryClient]);

  useEffect(() => cancelSelection, [cancelSelection]);

  return {
    activeThreadId,
    messages: detail?.messages ?? [],
    threadStatus: draft.state.activity ? draft.state.activity.threadStatus : detail?.status ?? null,
    phase: draft.state.activity?.phase ?? phaseForThread(detail),
    input: draft.state.input,
    postAnswerAction: draft.state.postAnswerAction,
    pendingFollowUp: draft.state.pendingFollowUp,
    queryError: draft.state.queryError,
    changeInput: draft.changeInput,
    changePostAnswerAction: draft.changePostAnswerAction,
    reportError: draft.reportError,
    getPendingSubmission: draft.getPendingSubmission,
    beginSubmission: draft.beginSubmission,
    failSubmission: draft.failSubmission,
    getSelection, getActiveThreadId, isCurrentSelection, selectThread,
    monitorThread, acceptSubmission, upsertThread,
    clearSelection, suspendThread, restoreThread, removeThread,
  };
}

export type ChatSession = ReturnType<typeof useChatThreadSelection>;
