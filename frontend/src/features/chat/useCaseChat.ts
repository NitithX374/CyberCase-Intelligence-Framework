"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  getApiErrorMessage,
  getCaseChat,
  type CaseChatDetail,
  type CaseChatStatus,
  type CaseRead,
  type ChatMessageRead,
} from "@/lib/api";
import { caseQueryKeys } from "@/hooks/useCaseQueries";
import type { RunPhase } from "@/components/common/types";
import {
  activeCaseChatFollowUp,
} from "@/lib/chat-followup";
import { determineCaseChatPhase, useChatDraft } from "./useChatDraft";
import { useCaseChatSubmission } from "./useCaseChatSubmission";

export interface UseCaseChatOptions {
  caseId: string | null;
  isChatOpen?: boolean;
  currentCase?: CaseRead | null;
  cases?: CaseRead[];
  upsertCase?: (caseRecord: CaseRead) => void;
}

export function useCaseChat({
  caseId: routeCaseId,
  isChatOpen = true,
  currentCase,
  cases,
  upsertCase,
}: UseCaseChatOptions) {
  const queryClient = useQueryClient();
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [prevRouteCaseId, setPrevRouteCaseId] = useState<string | null>(routeCaseId);

  if (prevRouteCaseId !== routeCaseId) {
    setPrevRouteCaseId(routeCaseId);
    setSelectedCaseId(null);
  }

  const effectiveCaseId = selectedCaseId ?? routeCaseId;
  const draft = useChatDraft();

  // Route-driven declarative query
  const chatQuery = useQuery<CaseChatDetail>({
    queryKey: caseQueryKeys.chat(effectiveCaseId ?? "none"),
    queryFn: async ({ signal }) => {
      const response = await getCaseChat(effectiveCaseId!, signal);
      return {
        ...response,
        messages: [...response.messages].sort((a, b) => a.ordinal - b.ordinal),
      };
    },
    enabled: Boolean(effectiveCaseId) && isChatOpen,
    retry: false,
    staleTime: 0,
  });

  const detail = chatQuery.data;

  // Synchronize draft state on case change
  const selectDraft = draft.selectDraft;
  const clearDraft = draft.clearDraft;
  useEffect(() => {
    if (effectiveCaseId) {
      selectDraft(effectiveCaseId);
    } else {
      clearDraft();
    }
  }, [clearDraft, effectiveCaseId, selectDraft]);

  // Capture query error in draft state
  const reportError = draft.reportError;
  useEffect(() => {
    if (chatQuery.error) {
      reportError(getApiErrorMessage(chatQuery.error, "The Case Chat could not be loaded."));
    }
  }, [chatQuery.error, reportError]);

  // Reconcile draft when chatQuery refreshes after a run settles via useCaseRunPolling.
  // Uses getPendingSubmission (ref-based) rather than activity state because reconcile
  // clears activity on every call, while the pending ref persists until completion.
  const reconcile = draft.reconcile;
  const getPending = draft.getPendingSubmission;
  useEffect(() => {
    if (detail && getPending()) {
      reconcile(detail);
    }
  }, [detail, reconcile, getPending]);

  const persistedFollowUp = useMemo(() => (
    detail ? activeCaseChatFollowUp(detail.messages, detail.status) : null
  ), [detail]);

  const pendingFollowUpItem = useMemo(() => (
    draft.state.pendingFollowUp ?? (
      detail && persistedFollowUp
        ? { caseId: detail.case_id, followUp: persistedFollowUp }
        : null
    )
  ), [detail, draft.state.pendingFollowUp, persistedFollowUp]);

  const messages: ChatMessageRead[] = useMemo(
    () => detail?.messages ?? [],
    [detail?.messages],
  );
  const chatStatus: CaseChatStatus | null = draft.state.activity
    ? draft.state.activity.chatStatus
    : detail?.status ?? null;
  const phase: RunPhase = draft.state.activity?.phase ?? determineCaseChatPhase(detail);

  const resolvedCase = currentCase ?? (
    cases && effectiveCaseId
      ? cases.find((c) => c.id === effectiveCaseId) ?? null
      : null
  );

  const submission = useCaseChatSubmission({
    caseId: effectiveCaseId,
    draft,
    messages,
    chatStatus,
    phase,
    pendingFollowUp: pendingFollowUpItem,
    currentCase: resolvedCase,
    upsertCase,
  });

  const selectCaseChat = useCallback(async (targetCaseId: string) => {
    setSelectedCaseId(targetCaseId);
    draft.selectDraft(targetCaseId);
    if (targetCaseId === effectiveCaseId) {
      await queryClient.refetchQueries({
        queryKey: caseQueryKeys.chat(targetCaseId),
        exact: true,
      });
    }
  }, [draft, effectiveCaseId, queryClient]);

  const suspendCaseChat = useCallback((id: string) => {
    const wasActive = effectiveCaseId === id;
    if (wasActive) {
      void queryClient.cancelQueries({ queryKey: caseQueryKeys.chat(id), exact: true });
    }
    return wasActive;
  }, [effectiveCaseId, queryClient]);

  return {
    ...submission,
    activeCaseChatId: effectiveCaseId,
    messages,
    input: draft.state.input,
    changeInput: draft.changeInput,
    chatStatus,
    phase,
    pendingFollowUp: pendingFollowUpItem ? pendingFollowUpItem.followUp : null,
    pendingFollowUpItem,
    queryError: draft.state.queryError,
    reportError: draft.reportError,
    isLoading: chatQuery.isLoading,
    isFetching: chatQuery.isFetching,
    refetch: chatQuery.refetch,
    selectCaseChat,
    suspendCaseChat,
    getPendingSubmission: draft.getPendingSubmission,
    draft,
  };
}
