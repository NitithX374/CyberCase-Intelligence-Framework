"use client";

import { usePathname, useRouter, useParams } from "next/navigation";
import { useCallback, useMemo, useState, type ReactNode } from "react";
import { detectResponseLanguage, getApiErrorMessage, type CaseRead } from "@/lib/api";
import type { WorkspaceView } from "@/features/workspace/routes";
import { useCase, useCaseMutations, useCases } from "@/features/cases/queries";
import { useCaseSources } from "@/features/sources/queries";
import { useIsCaseAnalysisRunning, useStartCaseAnalysis } from "@/features/analysis/queries";
import { casePath, caseRouteState } from "@/features/workspace/routes";
import { useCaseDeletion } from "@/features/cases/useCaseDeletion";
import { WorkspaceHeader } from "@/features/workspace/WorkspaceHeader";
import { WorkspaceChatPanel } from "@/features/chat/WorkspaceChatPanel";
import { DeleteCaseDialog } from "@/features/cases/DeleteCaseDialog";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/userFacingError";
import { WorkspaceActivityProvider } from "@/features/workspace/WorkspaceActivityContext";

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
  const [isFollowupPending, setIsFollowupPending] = useState(false);

  const casesQuery = useCases();
  const caseQuery = useCase(caseId ?? null);
  const sourcesQuery = useCaseSources(caseId ?? null);
  const { createMutation, deleteMutation, updateMutation } = useCaseMutations();
  const cases = useMemo(() => casesQuery.data ?? [], [casesQuery.data]);
  const activeCase = caseQuery.data ?? null;

  const sources = useMemo(() => sourcesQuery.data ?? [], [sourcesQuery.data]);
  const startAnalysis = useStartCaseAnalysis(caseId ?? null);
  const isAnalysisRunning = useIsCaseAnalysisRunning(caseId ?? null);

  const setChatOpen = useCallback((next: boolean) => {
    setIsChatOpen(next);
    try {
      localStorage.setItem(CHAT_OPEN_STORAGE_KEY, String(next));
    } catch {}
  }, []);
  const openChat = useCallback(() => setChatOpen(true), [setChatOpen]);
  const closeChat = useCallback(() => setChatOpen(false), [setChatOpen]);
  const toggleChat = useCallback(() => setChatOpen(!isChatOpen), [isChatOpen, setChatOpen]);

  const runAnalysis = useCallback(async () => {
    if (!caseId || isAnalysisRunning) return;
    try {
      const step = await startAnalysis.mutateAsync({
        response_language: detectResponseLanguage(
          sources.map((source) => source.exact_text).join("\n"),
        ),
      });
      if (step.status === "need_followup") {
        openChat();
        return;
      }
      router.push(casePath(caseId, "analysis"));
    } catch (error) {
      setChatActionError(getApiErrorMessage(error, "The Case analysis could not be started."));
    }
  }, [caseId, isAnalysisRunning, openChat, router, sources, startAnalysis]);
  const requestAnalysis = useCallback(() => void runAnalysis(), [runAnalysis]);

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

  return (
    <div className="flex h-dvh overflow-hidden bg-surface text-ink">
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden bg-surface">
        <WorkspaceHeader
          activeCase={activeCase}
          activeView={activeView}
          creatingCase={createMutation.isPending}
          isAnalyzing={isAnalysisRunning || isFollowupPending}
          isStale={activeCase?.analysis_freshness === "stale"}
          onViewChange={handleViewChange}
          onNewCase={handleNewCase}
          onRenameCase={(title) => void renameCase(title)}
          isChatOpen={isChatOpen}
          onToggleChat={() => void toggleChat()}
        />
        <main className="relative flex min-w-0 flex-1 flex-col overflow-y-auto bg-surface">
          <WorkspaceActivityProvider
            isFollowupPending={isFollowupPending}
            runAnalysis={requestAnalysis}
          >
            {children}
          </WorkspaceActivityProvider>
        </main>
      </div>

      <WorkspaceChatPanel
        caseId={caseId ?? null}
        isOpen={isChatOpen}
        onOpenChat={openChat}
        onCloseChat={closeChat}
        onViewChange={handleViewChange}
        onActivityChange={setIsFollowupPending}
      />

      <DeleteCaseDialog
        caseRecord={deleteCandidate}
        isDeleting={deleteMutation.isPending}
        onCancel={cancelDelete}
        onConfirm={() => void confirmDelete()}
      />
      <MeaningfulErrorModal
        isOpen={Boolean(chatActionError)}
        error={chatActionError ? toUserFacingError(chatActionError) : null}
        onClose={() => setChatActionError(null)}
      />
    </div>
  );
}
