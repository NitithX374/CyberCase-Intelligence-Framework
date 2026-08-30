export const chatQueryKeys = {
  all: ["chat"] as const,
  threads: () => [...chatQueryKeys.all, "threads"] as const,
  thread: (threadId: string) =>
    [...chatQueryKeys.threads(), threadId] as const,
  reports: (threadId: string) =>
    [...chatQueryKeys.thread(threadId), "reports"] as const,
};
