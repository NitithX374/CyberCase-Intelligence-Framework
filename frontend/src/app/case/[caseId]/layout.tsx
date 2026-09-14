"use client";

import { usePathname, useRouter, useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  getApiErrorMessage,
  type CaseRead,
  type ChatThreadDetail,
  type ChatThreadRead,
} from "@/lib/api";
import type { RunPhase, WorkspaceView } from "@/components/common/types";
import { chatTranscriptMessages } from "@/lib/chat-followup";
import { useCaseMutations, useCases } from "@/hooks/useCaseQueries";
import { useCaseRunPolling } from "@/hooks/useCaseRunPolling";
import { chatQueryKeys } from "@/hooks/useChatQueries";
import { casePath, caseRouteState } from "@/features/chat/routing/workspaceRoutes";
import { useChatSubmission } from "@/features/chat/runs/useChatSubmission";
import { useChatThreadSelection } from "@/features/chat/workspace/use-chat-thread-selection";
import { useChatThreadDeletion } from "@/features/chat/workspace/use-chat-thread-deletion";
import { useWorkspaceSubmissionActions } from "@/features/chat/workspace/use-workspace-submission-actions";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import { WorkspaceSidebar } from "@/components/layout/WorkspaceSidebar";
import { WorkspaceChatPanel } from "@/components/conversation/WorkspaceChatPanel";
import { DeleteCaseDialog } from "@/components/common/DeleteDialog";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/user-facing-error";
import { ensureCaseChat } from "@/lib/caseClient";

interface CaseShellLayoutProps {
  children: ReactNode;
}

export default function CaseShellLayout({ children }: CaseShellLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const params = useParams();
  const queryClient = useQueryClient();

  const caseId = (params?.caseId as string | undefined) ?? caseRouteState(pathname).caseId;
  const activeView = caseRouteState(pathname).view;

  const [deleteCandidate, setDeleteCandidate] = useState<CaseRead | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatActionError, setChatActionError] = useState<string | null>(null);

  const casesQuery = useCases();
  const { upsertCase, createMutation, updateMutation, deleteMutation } = useCaseMutations();
  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const activeCase = cases.find((c) => c.id === caseId) ?? null;

  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunPolling(
    caseId ?? null,
    runId,
    activeCase?.chat_thread_id,
  );
  const runStatus = runQuery.data?.status ?? caseRunStatus(activeCase);

  const cacheUpsertCaseFromChat = useCallback(
    (thread: ChatThreadRead) => {
      queryClient.setQueryData<ChatThreadDetail>(chatQueryKeys.detail(thread.id), (current) =>
        current ? { ...current, ...thread } : undefined,
      );
    },
    [queryClient],
  );

  const session = useChatThreadSelection({
    cacheUpsertThread: cacheUpsertCaseFromChat,
  });

  const {
    getActiveThreadId,
    messages,
    input,
    queryError,
    selectThread,
    refreshThread,
    clearSelection,
    changeInput,
  } = session;

  const latestAnalysisId = activeCase?.latest_analysis_result_id;
  const lastRefreshedAnalysisRef = useRef<string | null>(null);
  const lastCompletedRunRef = useRef<string | null>(null);

  useEffect(() => {
    if (!isChatOpen || !activeCase?.chat_thread_id || !latestAnalysisId) return;
    if (lastRefreshedAnalysisRef.current === latestAnalysisId) return;
    lastRefreshedAnalysisRef.current = latestAnalysisId;
    void refreshThread(activeCase.chat_thread_id);
  }, [activeCase?.chat_thread_id, isChatOpen, latestAnalysisId, refreshThread]);

  useEffect(() => {
    if (!isChatOpen || !activeCase?.chat_thread_id || runStatus !== "completed" || !runId) return;
    if (lastCompletedRunRef.current === runId) return;
    lastCompletedRunRef.current = runId;
    void refreshThread(activeCase.chat_thread_id);
  }, [activeCase?.chat_thread_id, isChatOpen, runStatus, refreshThread, runId]);

  useEffect(() => {
    if (!activeCase) return;
    const threadId = activeCase?.chat_thread_id ?? null;
    if (!isChatOpen || !threadId) {
      if (getActiveThreadId() !== null) clearSelection();
      return;
    }
    if (getActiveThreadId() !== threadId) void selectThread(threadId);
  }, [activeCase, clearSelection, getActiveThreadId, isChatOpen, selectThread]);

  const toggleChat = useCallback(async () => {
    if (isChatOpen) {
      setIsChatOpen(false);
      clearSelection();
      return;
    }
    setChatActionError(null);
    setIsChatOpen(true);
    if (!caseId) return;
    try {
      const threadId = activeCase?.chat_thread_id ?? (await ensureCaseChat(caseId)).id;
      if (!activeCase?.chat_thread_id) {
        const current = activeCase ?? { id: caseId, title: "New case", status: "idle", chat_thread_id: threadId, evidence_revision: 0, processing_status: "idle", has_pending_clarification: false, analysis_freshness: "missing", created_at: "", updated_at: "" };
        upsertCase({ ...current, chat_thread_id: threadId });
      }
      await selectThread(threadId);
    } catch (error) {
      setIsChatOpen(false);
      setChatActionError(getApiErrorMessage(error, "The Case Chat could not be opened."));
    }
  }, [activeCase, caseId, clearSelection, isChatOpen, selectThread, upsertCase]);

  const handleSelectCase = useCallback(
    (targetCaseId: string) => {
      router.push(casePath(targetCaseId, activeView));
      if (isChatOpen) {
        const selected = cases.find((c) => c.id === targetCaseId);
        if (selected?.chat_thread_id) void selectThread(selected.chat_thread_id);
        else clearSelection();
      }
    },
    [activeView, cases, clearSelection, isChatOpen, router, selectThread],
  );

  const handleNewCase = useCallback(async () => {
    if (createMutation.isPending) return;
    clearSelection();
    setIsChatOpen(false);
    try {
      const caseRecord = await createMutation.mutateAsync();
      router.push(casePath(caseRecord.id, "intake"));
    } catch {
      return;
    }
  }, [clearSelection, createMutation, router]);

  const handleViewChange = useCallback(
    (view: WorkspaceView) => {
      if (caseId) router.push(casePath(caseId, view));
    },
    [caseId, router],
  );

  const { submitContent } = useChatSubmission({
    session,
    cases,
    upsertCase,
    updateCase: (inputValue) => updateMutation.mutateAsync(inputValue),
    caseId: caseId ?? null,
    pendingClarificationId: null,
  });

  const { cancelDelete, confirmDelete } = useChatThreadDeletion({
    session,
    deleteCandidate,
    deletingCaseId: deleteMutation.isPending ? deleteMutation.variables ?? null : null,
    activeView,
    activeCaseId: caseId ?? null,
    isChatOpen,
    cases,
    deleteCase: (id) => deleteMutation.mutateAsync(id),
    router,
    setDeleteCandidate,
  });

  const visibleMessages = chatTranscriptMessages(messages);
  const {
    clearQueryError: handleClearQueryError,
    retryQuery: handleRetryQuery,
    submitMessage: handleSubmit,
  } = useWorkspaceSubmissionActions({
    session,
    submitContent,
  });

  const visibleWorkspaceError = chatActionError ?? queryError;
  const clearWorkspaceError = useCallback(() => {
    setChatActionError(null);
    handleClearQueryError();
  }, [handleClearQueryError]);

  const workspaceThreadStatus = caseThreadStatus(activeCase, runStatus);
  const workspacePhase = determineCaseRunPhase(runStatus, Boolean(activeCase?.latest_analysis_result_id));
  const casesError = casesQuery.error
    ? getApiErrorMessage(casesQuery.error, "Saved cases could not be loaded.")
    : createMutation.error
      ? getApiErrorMessage(createMutation.error, "A new case could not be created.")
      : deleteMutation.error
        ? getApiErrorMessage(deleteMutation.error, "The case could not be deleted.")
        : null;

  return (
    <div className="flex h-dvh overflow-hidden bg-surface text-ink">
      <WorkspaceSidebar
        cases={cases}
        activeCaseId={caseId ?? null}
        casesLoading={casesQuery.isLoading}
        casesError={casesError}
        onSelectCase={handleSelectCase}
        onNewCase={handleNewCase}
        onRequestDelete={setDeleteCandidate}
        deletingCaseId={deleteMutation.isPending ? deleteMutation.variables ?? null : null}
        activeView={activeView}
        onViewChange={handleViewChange}
      />

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden bg-surface">
        <WorkspaceHeader
          activeCase={activeCase}
          activeCaseId={caseId ?? null}
          activeView={activeView}
          cases={cases}
          creatingCase={createMutation.isPending}
          deletingCaseId={deleteMutation.isPending ? deleteMutation.variables ?? null : null}
          phase={workspacePhase}
          onViewChange={handleViewChange}
          onSelectCase={handleSelectCase}
          onNewCase={handleNewCase}
          onRequestDelete={setDeleteCandidate}
          isChatOpen={isChatOpen}
          onToggleChat={() => void toggleChat()}
        />

        <main className="flex min-w-0 flex-1 flex-col overflow-y-auto bg-surface">
          {children}
        </main>
      </div>

      <WorkspaceChatPanel
        isOpen={isChatOpen}
        phase={workspacePhase}
        messages={messages}
        visibleMessages={visibleMessages}
        threadStatus={workspaceThreadStatus}
        input={input}
        hasAnalysisContext={Boolean(activeCase?.latest_analysis_result_id)}
        onViewChange={handleViewChange}
        onNavigateToSource={() => handleViewChange("materials")}
        onInputChange={changeInput}
        onSubmit={handleSubmit}
        onToggleChat={() => void toggleChat()}
      />

      <DeleteCaseDialog
        caseRecord={deleteCandidate}
        isDeleting={deleteMutation.isPending}
        onCancel={cancelDelete}
        onConfirm={() => void confirmDelete()}
      />
      <MeaningfulErrorModal
        isOpen={Boolean(visibleWorkspaceError)}
        error={
          visibleWorkspaceError
            ? toUserFacingError(visibleWorkspaceError, {
                isUncertain: workspacePhase === "querying" || workspacePhase === "analyzing",
              })
            : null
        }
        onClose={clearWorkspaceError}
        onRetry={handleRetryQuery}
      />
    </div>
  );
}

function caseRunStatus(caseRecord: CaseRead | null): "queued" | "running" | "failed" | null {
  const status = caseRecord?.processing_status;
  return status === "queued" || status === "running" || status === "failed" ? status : null;
}

function caseThreadStatus(caseRecord: CaseRead | null, runStatus: string | null) {
  if (runStatus === "queued" || runStatus === "running") return "processing" as const;
  if (runStatus === "failed") return "failed" as const;
  return caseRecord?.status ?? null;
}

function determineCaseRunPhase(status: string | null, hasResult: boolean): RunPhase {
  if (status === "queued") return "querying";
  if (status === "running") return "analyzing";
  if (status === "failed") return "error";
  return hasResult ? "ready" : "idle";
}
