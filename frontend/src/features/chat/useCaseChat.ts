"use client";

import { useMutation, useMutationState, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, useState, type FormEvent } from "react";
import {
  createCaseChatMessage,
  getCaseChat,
  type CaseChatRead,
  type CaseRead,
  type ChatMessageRead,
} from "@/lib/api";
import { caseQueryKeys } from "@/lib/queryKeys";

interface Submission {
  content: string;
  key: string;
  answersQuestion: boolean;
  after: number;
}

export function useCaseChatQuery(caseId: string | null) {
  return useQuery<CaseChatRead>({
    queryKey: caseQueryKeys.chat(caseId ?? "none"),
    queryFn: async ({ signal }) => {
      const chat = await getCaseChat(caseId!, signal);
      return { ...chat, messages: inOrder(chat.messages ?? []) };
    },
    enabled: Boolean(caseId),
    retry: false,
    staleTime: 0,
  });
}

export function useCaseChat({ caseId }: { caseId: string | null }) {
  const queryClient = useQueryClient();
  const [input, setInput] = useState("");
  const [dismissedLoadError, setDismissedLoadError] = useState<number | null>(null);

  const [typedFor, setTypedFor] = useState(caseId);
  if (typedFor !== caseId) {
    setTypedFor(caseId);
    setInput("");
  }

  const chatQuery = useCaseChatQuery(caseId);
  const send = useMutation({
    mutationKey: caseQueryKeys.chatSend(caseId ?? "none"),
    mutationFn: ({ content, key }: Submission) => createCaseChatMessage(caseId!, content, key),
    onSuccess: (result) => {
      setInput("");
      queryClient.setQueryData<CaseChatRead>(caseQueryKeys.chat(caseId!), (current) =>
        current
          ? {
              ...current,
              messages: inOrder([...(current.messages ?? []), ...result.messages]),
              pending_question_id: result.pending_question_id ?? null,
            }
          : current,
      );
      if (result.analysis) {
        queryClient.setQueryData(caseQueryKeys.analysis(caseId!), result.analysis);
        queryClient.setQueryData<CaseRead>(caseQueryKeys.case(caseId!), (current) =>
          current
            ? {
                ...current,
                source_revision: result.analysis!.source_revision,
                latest_analysis_result_id: result.analysis!.id,
                analysis_freshness: result.analysis!.freshness,
              }
            : current,
        );
      }
    },
    onSettled: (_result, error) => {
      if (!caseId) return;
      void Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId), exact: true }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() }),
        ...(error
          ? [
              queryClient.invalidateQueries({ queryKey: caseQueryKeys.chat(caseId), exact: true }),
              queryClient.invalidateQueries({
                queryKey: caseQueryKeys.analysis(caseId),
                exact: true,
              }),
            ]
          : []),
      ]);
    },
  });

  const messages = useMemo(() => {
    const loaded = chatQuery.data?.messages ?? [];
    if (!send.isPending || !send.variables || !caseId) return loaded;
    if (alreadyStored(send.variables, loaded)) return loaded;
    return [...loaded, beingSent(caseId, send.variables, loaded)];
  }, [caseId, chatQuery.data, send.isPending, send.variables]);

  const pendingQuestionId = chatQuery.data?.pending_question_id ?? null;
  const loadError =
    chatQuery.error && chatQuery.errorUpdatedAt !== dismissedLoadError ? chatQuery.error : null;

  const submitContent = useCallback(
    (raw: string) => {
      const content = raw.trim();
      if (!caseId || !content || send.isPending) return;
      send.mutate({
        content,
        key: crypto.randomUUID(),
        answersQuestion: pendingQuestionId !== null,
        after: lastOrdinal(chatQuery.data?.messages ?? []),
      });
    },
    [caseId, chatQuery.data, pendingQuestionId, send],
  );

  return {
    messages,
    pendingQuestionId,
    isSending: send.isPending,
    isAnsweringQuestion: send.isPending && send.variables?.answersQuestion === true,
    input,
    changeInput: setInput,
    queryError: send.error ?? loadError,
    clearQueryError: useCallback(() => {
      if (send.error) send.reset();
      else setDismissedLoadError(chatQuery.errorUpdatedAt);
    }, [chatQuery.errorUpdatedAt, send]),
    retryQuery: useCallback(() => {
      if (send.error && send.variables) send.mutate(send.variables);
      else void chatQuery.refetch();
    }, [chatQuery, send]),
    submitContent,
    submitMessage: useCallback(
      (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        submitContent(input);
      },
      [input, submitContent],
    ),
  };
}

export function useIsFollowupPending(caseId: string | null): boolean {
  const answering = useMutationState({
    filters: {
      mutationKey: caseQueryKeys.chatSend(caseId ?? "none"),
      exact: true,
      status: "pending",
      predicate: (mutation) =>
        (mutation.state.variables as Submission | undefined)?.answersQuestion === true,
    },
    select: (mutation) => mutation.mutationId,
  });
  return caseId !== null && answering.length > 0;
}

function inOrder(messages: ChatMessageRead[]): ChatMessageRead[] {
  const byId = new Map(messages.map((message) => [message.id, message]));
  return [...byId.values()].sort((a, b) => a.ordinal - b.ordinal);
}

function lastOrdinal(messages: ChatMessageRead[]): number {
  return messages.reduce((highest, message) => Math.max(highest, message.ordinal), 0);
}

function alreadyStored(submission: Submission, loaded: ChatMessageRead[]): boolean {
  return loaded.some(
    (message) =>
      message.role === "user" &&
      message.ordinal > submission.after &&
      message.content === submission.content,
  );
}

function beingSent(
  caseId: string,
  submission: Submission,
  loaded: ChatMessageRead[],
): ChatMessageRead {
  return {
    id: `being-sent:${submission.key}`,
    case_id: caseId,
    ordinal: lastOrdinal(loaded) + 1,
    role: "user",
    content: submission.content,
    message_kind: "conversation",
    analysis_result_id: null,
    in_reply_to_message_id: null,
    metadata_json: {},
    created_at: new Date().toISOString(),
  };
}
