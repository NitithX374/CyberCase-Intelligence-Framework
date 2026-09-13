"use client";

import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  getApiErrorMessage,
  type CaseRead,
  type ChatThreadDetail,
  type ChatThreadRead,
} from "@/lib/api";
import type { RunPhase, WorkspaceView } from "@/components/common/types";
import { chatTranscriptMessages } from "@/lib/chat-followup";
import { ChatWorkspaceLayout } from "@/components/ChatWorkspaceLayout";
import { useCaseMutations, useCaseWorkspaceQueries, useCases } from "@/hooks/useCaseQueries";
import { useCaseRunPolling } from "@/hooks/useCaseRunPolling";
import { chatQueryKeys } from "@/hooks/useChatQueries";
import { casePath, caseRouteState } from "@/features/chat/routing/workspaceRoutes";
import { useChatSubmission } from "@/features/chat/runs/useChatSubmission";
import { useChatThreadSelection } from "@/features/chat/workspace/use-chat-thread-selection";
import { useChatThreadDeletion } from "@/features/chat/workspace/use-chat-thread-deletion";
import { useWorkspaceSubmissionActions } from "@/features/chat/workspace/use-workspace-submission-actions";
import { useCaseWorkspaceActions } from "@/hooks/useCaseWorkspaceActions";

export function ChatWorkspace() {
  const pathname = usePathname();
  const router = useRouter();
  const queryClient = useQueryClient();
  const routeState = caseRouteState(pathname);
  const routeCaseId = routeState.caseId;
  const [activeView, setActiveView] = useState<WorkspaceView>(routeState.view);
  const [activeViewPathname, setActiveViewPathname] = useState(pathname);
  if (activeViewPathname !== pathname) {
    setActiveViewPathname(pathname);
    setActiveView(routeState.view);
  }
  const [deleteCandidate, setDeleteCandidate] = useState<CaseRead | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const rootBootstrapDoneRef = useRef(false);

  const casesQuery = useCases();
  const { upsertCase, createMutation, updateMutation, deleteMutation } = useCaseMutations();
  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const activeCaseId = routeCaseId;
  const activeCase = cases.find((caseRecord) => caseRecord.id === activeCaseId) ?? null;
  const isInvalidCase = casesQuery.isSuccess && activeCaseId !== null && !activeCase;
  const caseData = useCaseWorkspaceQueries(isInvalidCase ? null : activeCaseId);
  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunPolling(
    isInvalidCase ? null : activeCaseId,
    runId,
    activeCase?.chat_thread_id,
  );
  const analysisResult = caseData.analysis.data ?? null;
  const runStatus = runQuery.data?.status ?? caseRunStatus(activeCase);

  const cacheUpsertCaseFromChat = useCallback((thread: ChatThreadRead) => {
    queryClient.setQueryData<ChatThreadDetail>(chatQueryKeys.detail(thread.id), (current) =>
      current ? { ...current, ...thread } : undefined
    );
  }, [queryClient]);
  const session = useChatThreadSelection({
    cacheUpsertThread: cacheUpsertCaseFromChat,
  });
  const {
    getActiveThreadId, messages, input,
    queryError, selectThread, refreshThread, clearSelection, changeInput,
  } = session;
  const actions = useCaseWorkspaceActions({
    activeCaseId,
    activeCase,
    isChatOpen,
    setIsChatOpen,
    session,
    upsertCase,
    updateCase: updateMutation.mutateAsync,
    router,
    setActiveView,
  });

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
  }, [activeCase, clearSelection, getActiveThreadId, isChatOpen, selectThread, activeCase?.chat_thread_id]);

  useEffect(() => {
    if (casesQuery.isLoading) return;
    if (routeCaseId === null) {
      if (!cases[0] || rootBootstrapDoneRef.current) return;
      rootBootstrapDoneRef.current = true;
      router.replace(casePath(cases[0].id, "overview"));
    } else if (!activeCase) {
      if (cases[0]) {
        router.replace(casePath(cases[0].id, activeView));
      } else {
        router.replace("/case");
      }
    }
  }, [activeCase, activeView, cases, casesQuery.isLoading, routeCaseId, router]);

  const handleViewChange = useCallback((view: WorkspaceView) => {
    setActiveView(view);
    if (activeCaseId) router.push(casePath(activeCaseId, view));
  }, [activeCaseId, router]);

  const handleSelectCase = useCallback(async (caseId: string) => {
    const selected = cases.find((caseRecord) => caseRecord.id === caseId);
    router.push(casePath(caseId, activeView));
    if (isChatOpen && selected?.chat_thread_id) await selectThread(selected.chat_thread_id);
    else clearSelection();
  }, [activeView, cases, clearSelection, isChatOpen, router, selectThread]);

  const handleNewCase = useCallback(async () => {
    if (createMutation.isPending) return;
    rootBootstrapDoneRef.current = true;
    clearSelection();
    setIsChatOpen(false);
    try {
      const caseRecord = await createMutation.mutateAsync();
      setActiveView("intake");
      router.push(casePath(caseRecord.id, "intake"));
    } catch {
      return;
    }
  }, [clearSelection, createMutation, router]);

  const pendingClarification = caseData.clarifications.data?.find((c) => c.state === "pending");
  const pendingClarificationId = pendingClarification?.id ?? pendingClarification?.question_message_id ?? null;

  const { submitContent } = useChatSubmission({
    session,
    cases,
    upsertCase,
    updateCase: (inputValue) => updateMutation.mutateAsync(inputValue),
    caseId: activeCaseId,
    pendingClarificationId,
  });
  const { cancelDelete, confirmDelete } = useChatThreadDeletion({
    session,
    deleteCandidate,
    deletingCaseId: deleteMutation.isPending ? deleteMutation.variables ?? null : null,
    activeView,
    activeCaseId,
    isChatOpen,
    cases,
    deleteCase: (caseId) => deleteMutation.mutateAsync(caseId),
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

  const workspaceError = actions.actionError ?? queryError;
  const caseDataError = caseData.documents.error
    ? getApiErrorMessage(caseData.documents.error, "Case documents could not be loaded.")
    : caseData.evidence.error
      ? getApiErrorMessage(caseData.evidence.error, "Admitted case evidence could not be loaded.")
      : caseData.analysis.error
        ? getApiErrorMessage(caseData.analysis.error, "Case analysis could not be loaded.")
        : caseData.snapshot.error
          ? getApiErrorMessage(caseData.snapshot.error, "The case evidence snapshot could not be loaded.")
          : caseData.clarifications.error
            ? getApiErrorMessage(caseData.clarifications.error, "Case clarification state could not be loaded.")
            : null;
  const visibleWorkspaceError = workspaceError ?? caseDataError;
  const clearWorkspaceError = useCallback(() => {
    actions.clearActionError();
    handleClearQueryError();
  }, [actions, handleClearQueryError]);
  const retryWorkspace = useCallback(() => {
    if (actions.actionError) actions.clearActionError();
    else handleRetryQuery();
  }, [actions, handleRetryQuery]);
  const workspaceThreadStatus = caseThreadStatus(activeCase, runStatus);
  const workspacePhase = determineCaseRunPhase(runStatus, analysisResult?.status === "validated");
  const casesError = casesQuery.error
    ? getApiErrorMessage(casesQuery.error, "Saved cases could not be loaded.")
    : createMutation.error
      ? getApiErrorMessage(createMutation.error, "A new case could not be created.")
      : deleteMutation.error
        ? getApiErrorMessage(deleteMutation.error, "The case could not be deleted.")
        : null;

  return (
    <ChatWorkspaceLayout
      activeCase={activeCase}
      activeCaseId={activeCaseId}
      activeView={activeView}
      cases={cases}
      casesLoading={casesQuery.isLoading}
      casesError={casesError}
      creatingCase={createMutation.isPending}
      deletingCaseId={deleteMutation.isPending ? deleteMutation.variables ?? null : null}
      phase={workspacePhase}
      threadStatus={workspaceThreadStatus}
      queryError={visibleWorkspaceError}
      input={input}
      visibleMessages={visibleMessages}
      messages={messages}
      documents={caseData.documents.data ?? []}
      evidence={caseData.evidence.data ?? []}
      analysisResult={analysisResult}
      evidenceSnapshot={caseData.snapshot.data ?? null}
      run={runQuery.data ?? null}
      runStatus={runStatus}
      clarifications={caseData.clarifications.data ?? []}
      analysisLoading={caseData.analysis.isLoading}
      analysisSubmitting={actions.isSubmitting}
      caseDataLoading={caseData.documents.isLoading || caseData.evidence.isLoading || caseData.analysis.isLoading}
      snapshotLoading={caseData.snapshot.isLoading}
      isUploadingDocument={actions.isUploadingDocument}
      admittingExtractionId={actions.admittingExtractionId}
      deleteCandidate={deleteCandidate}
      onSelectCase={(caseId) => void handleSelectCase(caseId)}
      onNewCase={() => void handleNewCase()}
      onRequestDelete={setDeleteCandidate}
      onViewChange={handleViewChange}
      onInputChange={changeInput}
      onSubmit={handleSubmit}
      onSetDeleteCandidate={setDeleteCandidate}
      onCancelDelete={cancelDelete}
      onConfirmDelete={() => void confirmDelete()}
      onNavigateToSource={() => { handleViewChange("materials"); }}
      onSubmitCase={actions.submitCase}
      onClearQueryError={clearWorkspaceError}
      onRetryQuery={retryWorkspace}
      isChatOpen={isChatOpen}
      onToggleChat={() => void actions.toggleChat()}
      onUploadDocument={(file) => void actions.uploadDocument(file)}
      onAdmitExtraction={(documentId, extractionId) => void actions.admitExtraction(documentId, extractionId)}
    />
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
