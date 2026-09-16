"use client";

import { usePathname, useRouter, useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  getApiErrorMessage,
  type CaseRead,
  type CaseChatDetail,
  type CaseChatRead,
} from "@/lib/api";
import type { RunPhase, WorkspaceView } from "@/components/common/types";
import { chatTranscriptMessages } from "@/lib/chat-followup";
import {
  caseQueryKeys,
  useCaseAnalysis,
  useCaseEvidence,
  useCaseMutations,
  useCases,
  useCaseRunPolling,
} from "@/hooks/useCaseQueries";
import { casePath, caseRouteState } from "@/features/chat/routing/workspaceRoutes";
import { useCaseChatSubmission } from "@/features/chat/runs/useCaseChatSubmission";
import { useCaseChatSelection } from "@/features/chat/workspace/use-case-chat-selection";
import { useCaseDeletion } from "@/features/chat/workspace/use-case-deletion";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import { WorkspaceSidebar } from "@/components/layout/WorkspaceSidebar";
import { WorkspaceChatPanel } from "@/components/conversation/WorkspaceChatPanel";
import { DeleteCaseDialog } from "@/components/common/DeleteDialog";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/user-facing-error";

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
  const analysisQuery = useCaseAnalysis(caseId ?? null);
  const evidenceQuery = useCaseEvidence(caseId ?? null);
  const { upsertCase, createMutation, deleteMutation } = useCaseMutations();
  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const activeCase = cases.find((c) => c.id === caseId) ?? null;

  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunPolling(
    caseId ?? null,
    runId,
    caseId,
  );
  const runStatus = runQuery.data?.status ?? caseRunStatus(activeCase);

  const cacheUpsertCaseFromChat = useCallback(
    (chat: CaseChatRead) => {
      queryClient.setQueryData<CaseChatDetail>(caseQueryKeys.chat(chat.case_id), (current) =>
        current ? { ...current, ...chat } : undefined,
      );
    },
    [queryClient],
  );

  const session = useCaseChatSelection({
    cacheUpsertCaseChat: cacheUpsertCaseFromChat,
  });

  const {
    getActiveCaseChatId,
    messages,
    input,
    queryError,
    selectCaseChat,
    refreshCaseChat,
    clearSelection,
    changeInput,
  } = session;

  const latestAnalysisId = activeCase?.latest_analysis_result_id;
  const lastRefreshedAnalysisRef = useRef<string | null>(null);
  const lastCompletedRunRef = useRef<string | null>(null);

  useEffect(() => {
    if (!isChatOpen || !activeCase || !latestAnalysisId) return;
    if (lastRefreshedAnalysisRef.current === latestAnalysisId) return;
    lastRefreshedAnalysisRef.current = latestAnalysisId;
    void refreshCaseChat(activeCase.id);
  }, [activeCase, isChatOpen, latestAnalysisId, refreshCaseChat]);

  useEffect(() => {
    if (!isChatOpen || !activeCase || runStatus !== "completed" || !runId) return;
    if (lastCompletedRunRef.current === runId) return;
    lastCompletedRunRef.current = runId;
    void refreshCaseChat(activeCase.id);
  }, [activeCase, isChatOpen, refreshCaseChat, runId, runStatus]);

  useEffect(() => {
    if (!activeCase) return;
    if (!isChatOpen || !activeCase) {
      if (getActiveCaseChatId() !== null) clearSelection();
      return;
    }
    if (getActiveCaseChatId() !== activeCase.id) void selectCaseChat(activeCase.id);
  }, [activeCase, clearSelection, getActiveCaseChatId, isChatOpen, selectCaseChat]);

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
      await selectCaseChat(caseId);
    } catch (error) {
      setIsChatOpen(false);
      setChatActionError(getApiErrorMessage(error, "The Case Chat could not be opened."));
    }
  }, [caseId, clearSelection, isChatOpen, selectCaseChat]);

  const handleSelectCase = useCallback(
    (targetCaseId: string) => {
      router.push(casePath(targetCaseId, activeView));
      if (isChatOpen) {
        const selected = cases.find((c) => c.id === targetCaseId);
        if (selected) void selectCaseChat(targetCaseId);
        else clearSelection();
      }
    },
    [activeView, cases, clearSelection, isChatOpen, router, selectCaseChat],
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

  const {
    clearQueryError: handleClearQueryError,
    retryQuery: handleRetryQuery,
    submitMessage: handleSubmit,
    submitFollowUp: handleFollowUp,
  } = useCaseChatSubmission({
    session,
    cases,
    upsertCase,
    caseId: caseId ?? null,
  });

  const { cancelDelete, confirmDelete } = useCaseDeletion({
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
  const visibleWorkspaceError = chatActionError ?? queryError;
  const clearWorkspaceError = useCallback(() => {
    setChatActionError(null);
    handleClearQueryError();
  }, [handleClearQueryError]);

  const workspaceChatStatus = caseChatStatus(activeCase, runStatus);
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
        chatStatus={workspaceChatStatus}
        input={input}
        hasAnalysisContext={Boolean(activeCase?.latest_analysis_result_id)}
        leadResult={analysisQuery.data ?? null}
        evidenceSources={evidenceQuery.data ?? []}
        onViewChange={handleViewChange}
        onNavigateToSource={() => handleViewChange("materials")}
        onInputChange={changeInput}
        onSubmit={handleSubmit}
        pendingFollowUp={session.pendingFollowUp?.followUp ?? null}
        onSubmitFollowUp={handleFollowUp}
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

function caseChatStatus(caseRecord: CaseRead | null, runStatus: string | null) {
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
