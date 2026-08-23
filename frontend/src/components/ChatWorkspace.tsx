"use client";

import { usePathname, useRouter } from "next/navigation";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
} from "react";
import {
  getApiErrorMessage,
  type ChatMessageAction,
  type ChatThreadRead,
} from "@/lib/api";
import {
  type WorkspaceRouteView,
  type WorkspaceView,
} from "@/components/common/types";
import {
  activeChatFollowUpForThread,
  chatTranscriptMessages,
} from "@/lib/chat-followup";
import { ChatWorkspaceLayout } from "@/components/ChatWorkspaceLayout";
import {
  useChatThreadMutations,
  useChatThreads,
} from "@/hooks/use-chat-queries";
import { chatPath, chatRouteState } from "@/features/chat/routing/chat-route";
import { useChatSubmission } from "@/features/chat/runs/use-chat-submission";
import type { PendingChatSubmission } from "@/features/chat/workspace/chat-workspace-types";
import { useChatThreadSelection } from "@/features/chat/workspace/use-chat-thread-selection";
import { useChatThreadDeletion } from "@/features/chat/workspace/use-chat-thread-deletion";


export function ChatWorkspace() {
  const pathname = usePathname();
  const router = useRouter();
  const routeState = chatRouteState(pathname);
  const routeThreadId = routeState.threadId;
  const routeView = routeState.view;
  const [activeView, setActiveView] = useState<WorkspaceRouteView>(routeView);
  const [activeViewPathname, setActiveViewPathname] = useState(pathname);
  if (activeViewPathname !== pathname) {
    setActiveViewPathname(pathname);
    setActiveView(routeView);
  }
  const [deleteCandidate, setDeleteCandidate] = useState<ChatThreadRead | null>(
    null,
  );

  const threadsQuery = useChatThreads();
  const {
    upsertThread: cacheUpsertThread,
    createMutation,
    updateMutation,
    deleteMutation,
  } = useChatThreadMutations();
  const threads = useMemo(() => threadsQuery.data ?? [], [threadsQuery.data]);
  const threadsLoading = threadsQuery.isLoading;
  const creatingThread = createMutation.isPending;
  const deletingThreadId = deleteMutation.isPending
    ? deleteMutation.variables ?? null
    : null;
  const threadsError = threadsQuery.error
    ? getApiErrorMessage(threadsQuery.error, "Saved chats could not be loaded.")
    : createMutation.error
      ? getApiErrorMessage(createMutation.error, "A new chat could not be created.")
      : deleteMutation.error
        ? getApiErrorMessage(deleteMutation.error, "The chat could not be deleted.")
        : null;

  const deletedThreadIdsRef = useRef(new Set<string>());
  const pendingSubmissionRef = useRef<PendingChatSubmission | null>(null);
  const rootBootstrapDoneRef = useRef(false);
  const {
    activeThreadId,
    setActiveThreadId,
    activeThreadIdRef,
    selectionGenerationRef,
    pollControllerRef,
    messages,
    setMessages,
    threadStatus,
    setThreadStatus,
    phase,
    setPhase,
    input,
    setInput,
    pendingFollowUp,
    setPendingFollowUp,
    postAnswerAction,
    setPostAnswerAction,
    queryError,
    setQueryError,
    upsertThread,
    isCurrentSelection,
    applyThreadDetail,
    selectThread,
  } = useChatThreadSelection({
    cacheUpsertThread,
    deletedThreadIdsRef,
    pendingSubmissionRef,
  });

  useEffect(() => {
    if (routeThreadId !== null) rootBootstrapDoneRef.current = false;
    if (
      routeThreadId !== null &&
      activeThreadIdRef.current !== routeThreadId
    ) {
      void selectThread(routeThreadId);
    }
  }, [activeThreadIdRef, routeThreadId, selectThread]);

  useEffect(() => {
    if (
      threadsLoading ||
      routeThreadId !== null ||
      !threads[0] ||
      rootBootstrapDoneRef.current
    ) {
      return;
    }

    const firstThreadId = threads[0].id;
    rootBootstrapDoneRef.current = true;
    router.replace(chatPath(firstThreadId, "overview"));
    if (activeThreadIdRef.current !== firstThreadId) {
      void selectThread(firstThreadId);
    }
  }, [
    activeThreadIdRef,
    routeThreadId,
    router,
    selectThread,
    threads,
    threadsLoading,
  ]);

  const handleViewChange = useCallback(
    (view: WorkspaceView) => {
      setActiveView(view);
      const threadId = activeThreadIdRef.current;
      if (threadId !== null) router.push(chatPath(threadId, view));
    },
    [activeThreadIdRef, router],
  );

  const handleNavigateToSource = useCallback(() => {
    setActiveView("chat");
    const threadId = activeThreadIdRef.current;
    if (threadId !== null) router.push(chatPath(threadId, "chat"));
  }, [activeThreadIdRef, router]);

  const handleSelectThread = useCallback(
    async (threadId: string): Promise<void> => {
      router.push(chatPath(threadId, activeView));
      await selectThread(threadId);
    },
    [activeView, router, selectThread],
  );

  const handleNewChat = useCallback(async () => {
    if (creatingThread) return;
    setActiveView("intake");
    setPostAnswerAction(null);
    try {
      const thread = await createMutation.mutateAsync();
      router.push(chatPath(thread.id, "intake"));
      await selectThread(thread.id);
    } catch {
      return;
    }
  }, [creatingThread, createMutation, router, selectThread, setPostAnswerAction]);

  const { submitContent } = useChatSubmission({
    activeThreadIdRef,
    selectionGenerationRef,
    pollControllerRef,
    pendingSubmissionRef,
    messages,
    threads,
    phase,
    threadStatus,
    postAnswerAction,
    createThread: () => createMutation.mutateAsync(),
    updateThread: (input) => updateMutation.mutateAsync(input),
    router,
    chatPath,
    selectThread,
    isCurrentSelection,
    applyThreadDetail,
    upsertThread,
    setMessages,
    setPhase,
    setThreadStatus,
    setQueryError,
    setInput,
    setPendingFollowUp,
    setPostAnswerAction,
  });

  const { cancelDelete, confirmDelete } = useChatThreadDeletion({
    deleteCandidate,
    deletingThreadId,
    activeThreadIdRef,
    pollControllerRef,
    selectionGenerationRef,
    pendingSubmissionRef,
    deletedThreadIdsRef,
    activeView,
    threads,
    deleteThread: (threadId) => deleteMutation.mutateAsync(threadId),
    router,
    selectThread,
    setDeleteCandidate,
    setActiveThreadId,
    setPendingFollowUp,
    setPostAnswerAction,
    setMessages,
    setInput,
    setThreadStatus,
    setQueryError,
    setPhase,
  });

  const activeThread =
    threads.find((thread) => thread.id === activeThreadId) ?? null;
  const persistedFollowUp = activeChatFollowUpForThread(messages, threadStatus);
  const displayFollowUp =
    persistedFollowUp ??
    (pendingFollowUp?.threadId === activeThreadId
      ? pendingFollowUp.followUp
      : null);
  const visibleMessages = chatTranscriptMessages(messages);
  const handlePostAnswerActionChange = useCallback(
    (action: ChatMessageAction) => {
      if (threadStatus === "answered") setPostAnswerAction(action);
    },
    [setPostAnswerAction, threadStatus],
  );
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    submitContent(
      input,
      displayFollowUp ? "followup" : "message",
      displayFollowUp ?? undefined,
    );
  };

  const handleSubmitCase = useCallback(
    async ({ title, description }: { title?: string; description: string }) => {
      const currentThreadId = activeThreadIdRef.current;
      if (currentThreadId && title) {
        void updateMutation.mutateAsync({ threadId: currentThreadId, title }).catch(() => undefined);
      }
      submitContent(description, "message", undefined, () => {
        setActiveView("overview");
        if (currentThreadId !== null) router.push(chatPath(currentThreadId, "overview"));
      });
    },
    [activeThreadIdRef, router, submitContent, updateMutation],
  );

  const hasCompletedAnalysis = messages.some(
    (message) =>
      message.role === "assistant" &&
      message.metadata_json.analysis_kind === "grounded_main_analysis",
  );
  const activeWorkspaceView = activeView;

  return (
    <ChatWorkspaceLayout
      activeThread={activeThread}
      activeThreadId={activeThreadId}
      activeView={activeView}
      activeWorkspaceView={activeWorkspaceView}
      threads={threads}
      threadsLoading={threadsLoading}
      threadsError={threadsError}
      creatingThread={creatingThread}
      deletingThreadId={deletingThreadId}
      phase={phase}
      threadStatus={threadStatus}
      queryError={queryError}
      input={input}
      postAnswerAction={postAnswerAction}
      visibleMessages={visibleMessages}
      hasCompletedAnalysis={hasCompletedAnalysis}
      messages={messages}
      deleteCandidate={deleteCandidate}
      onSelectThread={(threadId) => void handleSelectThread(threadId)}
      onNewChat={() => void handleNewChat()}
      onRequestDelete={setDeleteCandidate}
      onViewChange={handleViewChange}
      onInputChange={setInput}
      onPostAnswerActionChange={handlePostAnswerActionChange}
      onSubmit={handleSubmit}
      onSetDeleteCandidate={setDeleteCandidate}
      onCancelDelete={cancelDelete}
      onConfirmDelete={() => void confirmDelete()}
      onNavigateToSource={handleNavigateToSource}
      onSubmitCase={handleSubmitCase}
    />
  );
}
