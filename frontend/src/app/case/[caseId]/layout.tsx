"use client";

import { usePathname, useRouter, useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { detectResponseLanguage, getApiErrorMessage, type CaseRead } from "@/lib/api";
import type { WorkspaceView } from "@/components/common/types";
import {
  useCase,
  useCaseAnalysis,
  useCaseSources,
  useCaseMutations,
  useCases,
  useStartCaseAnalysis,
} from "@/hooks/useCaseQueries";
import { casePath, caseRouteState } from "@/lib/workspaceRoutes";
import { useCaseChat } from "@/hooks/useCaseChat";
import { useCaseDeletion } from "@/hooks/useCaseDeletion";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import { WorkspaceChatPanel } from "@/components/chat/WorkspaceChatPanel";
import { DeleteCaseDialog } from "@/components/common/DeleteDialog";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/userFacingError";
import { WorkspaceActivityProvider } from "@/components/layout/WorkspaceActivityContext";

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
  const sourcesQuery = useCaseSources(caseId ?? null);
  const { createMutation, deleteMutation, updateMutation } = useCaseMutations();
  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const activeCase = caseQuery.data ?? null;

  const chat = useCaseChat({ caseId: caseId ?? null });
  const sources = useMemo(() => sourcesQuery.data ?? [], [sourcesQuery.data]);
  const startAnalysis = useStartCaseAnalysis(caseId ?? null);
  const isFollowupPending = chat.isAnsweringQuestion;

  // The analysis belongs to the case, not to one of its pages, so the header
  // runs it and every view can see it running.
  const runAnalysis = useCallback(async () => {
    if (!caseId || startAnalysis.isPending) return;
    try {
      await startAnalysis.mutateAsync({
        response_language: detectResponseLanguage(
          sources.map((source) => source.exact_text).join("\n"),
        ),
      });
      router.push(casePath(caseId, "overview"));
    } catch (error) {
      setChatActionError(getApiErrorMessage(error, "The Case analysis could not be started."));
    }
  }, [caseId, router, sources, startAnalysis]);

  const renameCase = useCallback(
    async (title: string) => {
      if (!caseId) return;
      try {
        await updateMutation.mutateAsync({ caseId, title });
      } catch (error) {
        setChatActionError(getApiErrorMessage(error, "The Case could not be renamed."));
      }
    },
    [caseId, updateMutation],
  );

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

  // A question the analysis left waiting is worth interrupting for, once. If
  // the reader closes the panel it stays closed until a different one arrives.
  const pendingQuestionId = chat.pendingQuestionId;
  const announcedQuestionRef = useRef<string | null>(null);
  useEffect(() => {
    if (!pendingQuestionId || announcedQuestionRef.current === pendingQuestionId) return;
    announcedQuestionRef.current = pendingQuestionId;
    setIsChatOpen(true);
  }, [pendingQuestionId]);

  const handleNewCase = useCallback(async () => {
    if (createMutation.isPending) return;
    setIsChatOpen(false);
    try {
      const caseRecord = await createMutation.mutateAsync();
      router.push(casePath(caseRecord.id, "sources"));
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
    deletingCaseId: deleteMutation.isPending ? (deleteMutation.variables ?? null) : null,
    activeView,
    activeCaseId: caseId ?? null,
    cases,
    deleteCase: (id) => deleteMutation.mutateAsync(id),
    router,
    setDeleteCandidate,
  });

  const visibleWorkspaceError = chatActionError ?? chat.queryError;
  const clearWorkspaceError = useCallback(() => {
    setChatActionError(null);
    chat.clearQueryError();
  }, [chat]);

  return (
    <div className="flex h-dvh overflow-hidden bg-surface text-ink">
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden bg-surface">
        <WorkspaceHeader
          activeCase={activeCase}
          activeView={activeView}
          creatingCase={createMutation.isPending}
          hasAnalysis={Boolean(activeCase?.latest_analysis_result_id)}
          canAnalyze={sources.length > 0}
          isAnalyzing={startAnalysis.isPending || isFollowupPending}
          isStale={activeCase?.analysis_freshness === "stale"}
          onAnalyze={() => void runAnalysis()}
          onViewChange={handleViewChange}
          onNewCase={handleNewCase}
          onRenameCase={(title) => void renameCase(title)}
          isChatOpen={isChatOpen}
          onToggleChat={() => void toggleChat()}
        />
        <main className="flex min-w-0 flex-1 flex-col overflow-y-auto bg-surface">
          <WorkspaceActivityProvider isFollowupPending={isFollowupPending}>
            {children}
          </WorkspaceActivityProvider>
        </main>
      </div>

      <WorkspaceChatPanel
        isOpen={isChatOpen}
        isSending={chat.isSending}
        messages={chat.messages}
        isAnsweringQuestion={isFollowupPending}
        input={chat.input}
        hasAnalysisContext={Boolean(activeCase?.latest_analysis_result_id)}
        leadResult={analysisQuery.data ?? null}
        sources={sourcesQuery.data ?? []}
        onViewChange={handleViewChange}
        onNavigateToSource={() => handleViewChange("sources")}
        onInputChange={chat.changeInput}
        onSubmit={chat.submitMessage}
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
                isUncertain: chat.isSending,
              })
            : null
        }
        onClose={clearWorkspaceError}
        onRetry={chat.retryQuery}
      />
    </div>
  );
}
