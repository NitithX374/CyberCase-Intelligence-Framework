import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { useCallback } from "react";
import {
  createChatThread,
  deleteChatThread,
  listChatThreads,
  updateChatThread,
  type ChatThreadRead,
} from "@/lib/api";
export const chatQueryKeys = {
  all: ["chat"] as const,
  threads: () => [...chatQueryKeys.all, "threads"] as const,
  thread: (threadId: string) =>
    [...chatQueryKeys.threads(), threadId] as const,
  detail: (threadId: string | null) =>
    [...chatQueryKeys.all, "threads", threadId, "detail"] as const,
  reports: (threadId: string) =>
    [...chatQueryKeys.thread(threadId), "reports"] as const,
};

function sortThreads(threads: ChatThreadRead[]): ChatThreadRead[] {
  return [...threads].sort(
    (left, right) => Date.parse(right.updated_at) - Date.parse(left.updated_at),
  );
}

export function useChatThreads() {
  return useQuery({
    queryKey: chatQueryKeys.threads(),
    queryFn: ({ signal }) => listChatThreads(signal),
    retry: false,
  });
}

export function useChatThreadMutations() {
  const queryClient = useQueryClient();

  const upsertThread = useCallback((thread: ChatThreadRead) => {
    queryClient.setQueryData<ChatThreadRead[]>(
      chatQueryKeys.threads(),
      (current) =>
        sortThreads([
          thread,
          ...(current ?? []).filter((item) => item.id !== thread.id),
        ]),
    );
  }, [queryClient]);

  const createMutation = useMutation({
    mutationFn: () => createChatThread(),
    onSuccess: upsertThread,
  });
  const updateMutation = useMutation({
    mutationFn: ({ threadId, title }: { threadId: string; title: string }) =>
      updateChatThread(threadId, title),
    onSuccess: upsertThread,
  });
  const deleteMutation = useMutation({
    mutationFn: (threadId: string) => deleteChatThread(threadId),
    onSuccess: (_value, threadId) => {
      queryClient.setQueryData<ChatThreadRead[]>(
        chatQueryKeys.threads(),
        (current) => (current ?? []).filter((thread) => thread.id !== threadId),
      );
      queryClient.removeQueries({ queryKey: chatQueryKeys.thread(threadId) });
    },
  });

  return {
    upsertThread,
    createMutation,
    updateMutation,
    deleteMutation,
  };
}
