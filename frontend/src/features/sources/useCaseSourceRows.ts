"use client";

import { useMemo } from "react";
import { useCaseChatQuery } from "@/features/chat/useCaseChat";
import { chatFollowups } from "@/features/citations/followupSources";
import { useCaseSources } from "./queries";

export function useCaseSourceRows(caseId: string | null) {
  const sourcesQuery = useCaseSources(caseId);
  const chatQuery = useCaseChatQuery(caseId);
  const sources = useMemo(() => sourcesQuery.data ?? [], [sourcesQuery.data]);
  const followups = useMemo(() => chatFollowups(chatQuery.data?.messages ?? []), [chatQuery.data]);
  const refetch = () => {
    if (sourcesQuery.isLoadingError) void sourcesQuery.refetch();
    if (chatQuery.isLoadingError) void chatQuery.refetch();
  };
  return {
    sources,
    followups,
    isError: sourcesQuery.isLoadingError || chatQuery.isLoadingError,
    refetch,
  };
}
