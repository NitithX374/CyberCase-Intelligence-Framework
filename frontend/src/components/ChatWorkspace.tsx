"use client";

import { usePathname, useRouter } from "next/navigation";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  getApiErrorMessage,
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
import { useChatThreadSelection } from "@/features/chat/workspace/use-chat-thread-selection";
import { useChatThreadDeletion } from "@/features/chat/workspace/use-chat-thread-deletion";
import { useWorkspaceSubmissionActions } from "@/features/chat/workspace/use-workspace-submission-actions";

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

  const rootBootstrapDoneRef = useRef(false);
  const session = useChatThreadSelection({ cacheUpsertThread });
  const {
    activeThreadId, getActiveThreadId, messages, threadStatus, phase, input,
    pendingFollowUp, postAnswerAction, queryError, selectThread, changeInput,
    changePostAnswerAction,
  } = session;

  useEffect(() => {
    if (routeThreadId !== null) rootBootstrapDoneRef.current = false;
    if (
      routeThreadId !== null &&
      getActiveThreadId() !== routeThreadId
    ) {
      void selectThread(routeThreadId);
    }
  }, [getActiveThreadId, routeThreadId, selectThread]);

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
    if (getActiveThreadId() !== firstThreadId) {
      void selectThread(firstThreadId);
    }
  }, [
    getActiveThreadId,
    routeThreadId,
    router,
    selectThread,
    threads,
    threadsLoading,
  ]);

  const handleViewChange = useCallback(
    (view: WorkspaceView) => {
      setActiveView(view);
      const threadId = getActiveThreadId();
      if (threadId !== null) router.push(chatPath(threadId, view));
    },
    [getActiveThreadId, router],
  );

  const handleNavigateToSource = useCallback(() => {
    setActiveView("chat");
    const threadId = getActiveThreadId();
    if (threadId !== null) router.push(chatPath(threadId, "chat"));
  }, [getActiveThreadId, router]);

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
    changePostAnswerAction(null);
    try {
      const thread = await createMutation.mutateAsync();
      router.push(chatPath(thread.id, "intake"));
      await selectThread(thread.id);
    } catch {
      return;
    }
  }, [creatingThread, createMutation, router, selectThread, changePostAnswerAction]);

  const { submitContent } = useChatSubmission({
    session,
    threads,
    createThread: () => createMutation.mutateAsync(),
    updateThread: (input) => updateMutation.mutateAsync(input),
    router,
    chatPath,
  });

  const { cancelDelete, confirmDelete } = useChatThreadDeletion({
    session,
    deleteCandidate,
    deletingThreadId,
    activeView,
    threads,
    deleteThread: (threadId) => deleteMutation.mutateAsync(threadId),
    router,
    setDeleteCandidate,
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
  const hasCompletedAnalysis = messages.some(
    (message) =>
      message.role === "assistant" &&
      message.metadata_json.analysis_kind === "grounded_main_analysis",
  );
  const {
    changePostAnswerAction: handlePostAnswerActionChange,
    clearQueryError: handleClearQueryError,
    retryQuery: handleRetryQuery,
    submitCase: handleSubmitCase,
    submitMessage: handleSubmit,
  } = useWorkspaceSubmissionActions({
    session,
    displayFollowUp,
    router,
    submitContent,
    updateTitle: updateMutation.mutateAsync,
    setActiveView,
  });

  return (
    <ChatWorkspaceLayout
      activeThread={activeThread}
      activeThreadId={activeThreadId}
      activeView={activeView}
      activeWorkspaceView={activeView}
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
      onInputChange={changeInput}
      onPostAnswerActionChange={handlePostAnswerActionChange}
      onSubmit={handleSubmit}
      onSetDeleteCandidate={setDeleteCandidate}
      onCancelDelete={cancelDelete}
      onConfirmDelete={() => void confirmDelete()}
      onNavigateToSource={handleNavigateToSource}
      onSubmitCase={handleSubmitCase}
      onClearQueryError={handleClearQueryError}
      onRetryQuery={handleRetryQuery}
    />
  );
}
