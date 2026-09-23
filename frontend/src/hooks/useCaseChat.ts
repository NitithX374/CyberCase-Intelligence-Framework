"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, useState, type FormEvent } from "react";
import {
  createCaseChatMessage,
  getApiErrorMessage,
  getCaseChat,
  type CaseChatDetail,
  type CaseRead,
  type ChatMessageRead,
} from "@/lib/api";
import { caseQueryKeys } from "@/hooks/useCaseQueries";

interface Submission {
  content: string;
  key: string;
  answersQuestion: boolean;
}

export function openQuestionId(messages: ChatMessageRead[]): string | null {
  const answered = new Set(messages.map((message) => message.in_reply_to_message_id));
  const latest = [...messages].reverse().find((m) => m.gap_key);
  return latest && !answered.has(latest.id) ? latest.id : null;
}

export function useCaseChatMessages({ caseId }: { caseId: string | null }) {
  return useQuery<CaseChatDetail>({
    queryKey: caseQueryKeys.chat(caseId ?? "none"),
    queryFn: async ({ signal }) => {
      const response = await getCaseChat(caseId!, signal);
      return { ...response, messages: inOrder(response.messages) };
    },
    enabled: Boolean(caseId),
    retry: false,
    staleTime: 0,
  });
}


export function useCaseChat({ caseId }: { caseId: string | null }) {
  const queryClient = useQueryClient();
  const [input, setInput] = useState("");
  const [dismissed, setDismissed] = useState<string | null>(null);

  const [typedFor, setTypedFor] = useState(caseId);
  if (typedFor !== caseId) {
    setTypedFor(caseId);
    setInput("");
  }

  const chatQuery = useCaseChatMessages({ caseId });
  const send = useMutation({
    mutationFn: ({ content, key }: Submission) => createCaseChatMessage(caseId!, content, key),
    onSuccess: (result) => {
      setInput("");
      queryClient.setQueryData<CaseChatDetail>(caseQueryKeys.chat(caseId!), (current) =>
        current
          ? { ...current, messages: inOrder([...current.messages, ...result.messages]) }
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
              status: "answered",
            }
            : current,
        );
      }
      void Promise.all([
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId!), exact: true }),
        queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() }),
      ]);
    },
  });

  const messages = useMemo(() => {
    const loaded = chatQuery.data?.messages ?? [];
    if (!send.isPending || !send.variables || !caseId)
      return loaded;
    return [...loaded, beingSent(caseId, send.variables, loaded)];
  }, [caseId, chatQuery.data?.messages, send.isPending, send.variables]);

  const pendingQuestionId = useMemo(() => openQuestionId(messages), [messages]);
  const failure = send.error
    ? getApiErrorMessage(send.error, "The message could not be submitted.")
    : chatQuery.error
      ? getApiErrorMessage(chatQuery.error, "The Case Chat could not be loaded.")
      : null;

  const submitContent = useCallback(
    (raw: string) => {
      const content = raw.trim();
      if (!caseId || !content || send.isPending) return;
      send.mutate({
        content,
        key: crypto.randomUUID(),
        answersQuestion: pendingQuestionId !== null,
      });
    },
    [caseId, pendingQuestionId, send],
  );

  return {
    messages,
    pendingQuestionId,
    isSending: send.isPending,
    isAnsweringQuestion: send.isPending && send.variables?.answersQuestion === true,
    input,
    changeInput: setInput,
    queryError: failure === dismissed ? null : failure,
    clearQueryError: useCallback(() => {
      send.reset();
      setDismissed(failure);
    }, [failure, send]),
    retryQuery: useCallback(() => {
      if (send.variables) send.mutate(send.variables);
    }, [send]),
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

function inOrder(messages: ChatMessageRead[]): ChatMessageRead[] {
  const byId = new Map(messages.map((message) => [message.id, message]));
  return [...byId.values()].sort((a, b) => a.ordinal - b.ordinal);
}

function beingSent(
  caseId: string,
  submission: Submission,
  loaded: ChatMessageRead[],
): ChatMessageRead {
  return {
    id: `being-sent:${submission.key}`,
    case_id: caseId,
    ordinal: loaded.reduce((highest, message) => Math.max(highest, message.ordinal), 0) + 1,
    role: "user",
    content: submission.content,
    message_kind: "conversation",
    analysis_result_id: null,
    in_reply_to_message_id: null,
    metadata_json: { action: "conversation" },
    created_at: new Date().toISOString(),
  };
}
