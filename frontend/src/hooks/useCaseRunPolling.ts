"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { getCaseRun, type CaseRunRead } from "@/lib/api";
import { chatQueryKeys } from "./useChatQueries";
import { caseQueryKeys } from "./useCaseQueries";

export function useCaseRunPolling(
  caseId: string | null,
  runId: string | null | undefined,
  chatThreadId: string | null | undefined,
) {
  const queryClient = useQueryClient();
  const lastInvalidated = useRef<string | null>(null);
  const query = useQuery<CaseRunRead>({
    queryKey: caseQueryKeys.run(caseId ?? "none", runId ?? "none"),
    queryFn: ({ signal }) => getCaseRun(caseId!, runId!, signal),
    enabled: Boolean(caseId && runId),
    retry: false,
    refetchInterval: (currentQuery) => {
      const status = currentQuery.state.data?.status;
      return status === "queued" || status === "running" ? 1500 : false;
    },
  });

  useEffect(() => {
    const status = query.data?.status;
    if (!caseId || !runId || (status !== "completed" && status !== "failed")) return;
    const attemptCount = query.data?.attempt_count ?? 0;
    const invalidationKey = `${runId}:${attemptCount}:${status}`;
    if (lastInvalidated.current === invalidationKey) return;
    lastInvalidated.current = invalidationKey;
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.cases() });
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.case(caseId) });
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.analysis(caseId) });
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.evidence(caseId) });
    void queryClient.invalidateQueries({ queryKey: caseQueryKeys.clarifications(caseId) });
    if (chatThreadId) {
      void queryClient.refetchQueries({
        queryKey: chatQueryKeys.detail(chatThreadId),
        exact: true,
        type: "all",
      });
    }
  }, [caseId, chatThreadId, query.data?.status, query.data?.attempt_count, queryClient, runId]);

  return query;
}
