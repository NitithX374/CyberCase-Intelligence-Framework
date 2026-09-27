"use client";

import { useParams, useRouter, useSelectedLayoutSegment } from "next/navigation";
import { useCallback, useState, type ReactNode } from "react";
import { casePath, type WorkspaceView } from "@/features/workspace/routes";
import { useCase, useCaseMutations } from "@/features/cases/queries";
import { useIsAnalysisUpdating } from "@/features/analysis/queries";
import { useAnalysisRunOutcome } from "@/features/analysis/useRunCaseAnalysis";
import { WorkspaceHeader } from "@/features/workspace/WorkspaceHeader";
import { WorkspaceChatPanel } from "@/features/chat/WorkspaceChatPanel";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/userFacingError";

const CHAT_OPEN_STORAGE_KEY = "cybercase:chat-open";

export function CaseWorkspace({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { caseId } = useParams<{ caseId: string }>();
  const activeView = (useSelectedLayoutSegment() ?? "analysis") as WorkspaceView;

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
  const [actionError, setActionError] = useState<unknown>(null);

  const activeCase = useCase(caseId).data ?? null;
  const { createMutation, updateMutation } = useCaseMutations();
  const isAnalyzing = useIsAnalysisUpdating(caseId);

  const setChatOpen = useCallback((next: boolean) => {
    setIsChatOpen(next);
    try {
      localStorage.setItem(CHAT_OPEN_STORAGE_KEY, String(next));
    } catch {}
  }, []);
  const openChat = useCallback(() => setChatOpen(true), [setChatOpen]);
  const closeChat = useCallback(() => setChatOpen(false), [setChatOpen]);

  useAnalysisRunOutcome(caseId, {
    onCompleted: () => router.push(casePath(caseId, "analysis")),
    onQuestion: openChat,
    onFailed: setActionError,
  });

  const renameCase = async (title: string) => {
    try {
      await updateMutation.mutateAsync({ caseId, title });
    } catch (error) {
      setActionError(error);
    }
  };

  const handleNewCase = async () => {
    if (createMutation.isPending) return;
    setChatOpen(false);
    try {
      const caseRecord = await createMutation.mutateAsync();
      router.push(casePath(caseRecord.id, "sources"));
    } catch (error) {
      setActionError(error);
    }
  };

  const handleViewChange = useCallback(
    (view: WorkspaceView) => router.push(casePath(caseId, view)),
    [caseId, router],
  );

  return (
    <div className="flex h-dvh overflow-hidden bg-surface text-ink">
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden bg-surface">
        <WorkspaceHeader
          activeCase={activeCase}
          activeView={activeView}
          creatingCase={createMutation.isPending}
          isAnalyzing={isAnalyzing}
          isStale={activeCase?.analysis_freshness === "stale"}
          onViewChange={handleViewChange}
          onNewCase={() => void handleNewCase()}
          onRenameCase={(title) => void renameCase(title)}
          isChatOpen={isChatOpen}
          onToggleChat={() => setChatOpen(!isChatOpen)}
        />
        <main className="relative flex min-w-0 flex-1 flex-col overflow-y-auto bg-surface">
          {children}
        </main>
      </div>

      <WorkspaceChatPanel
        caseId={caseId}
        isOpen={isChatOpen}
        onOpenChat={openChat}
        onCloseChat={closeChat}
        onViewChange={handleViewChange}
      />

      <MeaningfulErrorModal
        isOpen={actionError !== null}
        error={actionError !== null ? toUserFacingError(actionError) : null}
        onClose={() => setActionError(null)}
      />
    </div>
  );
}
