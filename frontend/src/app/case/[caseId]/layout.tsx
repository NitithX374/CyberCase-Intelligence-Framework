"use client";

import { usePathname, useRouter, useParams } from "next/navigation";
import { useCallback, useMemo, useState, type ReactNode } from "react";
import {
  getApiErrorMessage,
  type CaseRead,
} from "@/lib/api";
import type { RunPhase, WorkspaceView } from "@/components/common/types";
import { chatTranscriptMessages } from "@/lib/chat-followup";
import {
  useCase,
  useCaseAnalysis,
  useCaseEvidence,
  useCaseMutations,
  useCases,
  useCaseRunPolling,
} from "@/hooks/useCaseQueries";
import { casePath, caseRouteState } from "@/lib/workspaceRoutes";
import { useCaseChat } from "@/features/chat/useCaseChat";
import { useCaseDeletion } from "@/hooks/useCaseDeletion";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import { WorkspaceSidebar } from "@/components/layout/WorkspaceSidebar";
import { WorkspaceChatPanel } from "@/components/conversation/WorkspaceChatPanel";
import { DeleteCaseDialog } from "@/components/common/DeleteDialog";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/user-facing-error";

interface CaseShellLayoutProps {
  children: ReactNode;
}

const CHAT_OPEN_STORAGE_KEY = "cybercase:chat-open";

export default function CaseShellLayout({ children }: CaseShellLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const params = useParams();

  const caseId = (params?.caseId as string | undefined) ?? caseRouteState(pathname).caseId;
  const activeView = caseRouteState(pathname).view;

  const [deleteCandidate, setDeleteCandidate] = useState<CaseRead | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(() => {
    if (typeof window === "undefined") return false;
    try {
      const saved = localStorage.getItem(CHAT_OPEN_STORAGE_KEY);
      if (saved !== null) return saved === "true";
      return window.innerWidth >= 768;
    } catch {
      return false;
    }
  });
  const [chatActionError, setChatActionError] = useState<string | null>(null);

  const casesQuery = useCases();
  const caseQuery = useCase(caseId ?? null);
  const analysisQuery = useCaseAnalysis(caseId ?? null);
  const evidenceQuery = useCaseEvidence(caseId ?? null);
  const { upsertCase, createMutation, deleteMutation } = useCaseMutations();
  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const activeCase = caseQuery.data ?? null;

  const runId = activeCase?.active_run_id ?? activeCase?.latest_run_id ?? null;
  const runQuery = useCaseRunPolling(caseId ?? null, runId);
  const runStatus = runQuery.data?.status ?? caseRunStatus(activeCase);

  const chat = useCaseChat({
    caseId: caseId ?? null,
    isChatOpen,
    currentCase: activeCase,
    cases,
    upsertCase,
  });

  const toggleChat = useCallback(() => {
    setIsChatOpen((prev) => {
      const next = !prev;
      try {
        localStorage.setItem(CHAT_OPEN_STORAGE_KEY, String(next));
      } catch {
        // ignore
      }
      return next;
    });
  }, []);

  const handleSelectCase = useCallback(
    (targetCaseId: string) => {
      router.push(casePath(targetCaseId, activeView));
    },
    [activeView, router],
  );

  const handleNewCase = useCallback(async () => {
    if (createMutation.isPending) return;
    setIsChatOpen(false);
    try {
      const caseRecord = await createMutation.mutateAsync();
      router.push(casePath(caseRecord.id, "intake"));
    } catch {
      return;
    }
  }, [createMutation, router]);

  const handleViewChange = useCallback(
    (view: WorkspaceView) => {
      if (caseId) router.push(casePath(caseId, view));
    },
    [caseId, router],
  );

  const { cancelDelete, confirmDelete } = useCaseDeletion({
    deleteCandidate,
    deletingCaseId: deleteMutation.isPending ? deleteMutation.variables ?? null : null,
    activeView,
    activeCaseId: caseId ?? null,
    cases,
    deleteCase: (id) => deleteMutation.mutateAsync(id),
    router,
    setDeleteCandidate,
  });

  const visibleMessages = chatTranscriptMessages(chat.messages);
  const visibleWorkspaceError = chatActionError ?? chat.queryError;
  const clearWorkspaceError = useCallback(() => {
    setChatActionError(null);
    chat.clearQueryError();
  }, [chat]);

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
        messages={chat.messages}
        visibleMessages={visibleMessages}
        chatStatus={chat.chatStatus}
        input={chat.input}
        hasAnalysisContext={Boolean(activeCase?.latest_analysis_result_id)}
        leadResult={analysisQuery.data ?? null}
        evidenceSources={evidenceQuery.data ?? []}
        onViewChange={handleViewChange}
        onNavigateToSource={() => handleViewChange("materials")}
        onInputChange={chat.changeInput}
        onSubmit={chat.submitMessage}
        pendingFollowUp={chat.pendingFollowUp}
        onSubmitFollowUp={chat.submitFollowUp}
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
        onRetry={chat.retryQuery}
      />
    </div>
  );
}

function caseRunStatus(caseRecord: CaseRead | null): "queued" | "running" | "failed" | null {
  const status = caseRecord?.processing_status;
  return status === "queued" || status === "running" || status === "failed" ? status : null;
}


function determineCaseRunPhase(status: string | null, hasResult: boolean): RunPhase {
  if (status === "queued") return "querying";
  if (status === "running") return "analyzing";
  if (status === "failed") return "error";
  return hasResult ? "ready" : "idle";
}
