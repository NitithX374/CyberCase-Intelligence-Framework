"use client";

import { useParams, useRouter, useSelectedLayoutSegment } from "next/navigation";
import { useCallback, useState, type ReactNode } from "react";
import { casePath, type WorkspaceView } from "@/lib/casePaths";
import { useCase, useCaseMutations } from "@/features/cases/queries";
import { useAnalysisAvailability } from "@/features/analysis/queries";
import { useAnalysisRunOutcome, useRunCaseAnalysis } from "@/features/analysis/useRunCaseAnalysis";
import { CaseNotFound } from "@/features/workspace/CaseNotFound";
import { WorkspaceHeader } from "@/features/workspace/WorkspaceHeader";
import { CaseSidebar } from "@/features/workspace/CaseSidebar";
import { useCaseOverview } from "@/features/analysis/useCaseOverview";
import { WorkspaceChatPanel } from "@/features/chat/WorkspaceChatPanel";
import { MeaningfulErrorModal } from "@/components/MeaningfulErrorModal";
import { isCaseNotFound, toUserFacingError } from "@/lib/userFacingError";

const CHAT_OPEN_STORAGE_KEY = "cybercase:ask-open";

export function CaseWorkspace({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { caseId } = useParams<{ caseId: string }>();
  const activeView = (useSelectedLayoutSegment() ?? "analysis") as WorkspaceView;

  const [isChatOpen, setIsChatOpen] = useState(() => {
    if (typeof window === "undefined") return false;
    try {
      const saved = localStorage.getItem(CHAT_OPEN_STORAGE_KEY);
      return saved === "true";
    } catch {
      return false;
    }
  });
  const [actionError, setActionError] = useState<unknown>(null);

  const caseQuery = useCase(caseId);
  const activeCase = caseQuery.data ?? null;
  const { createMutation, updateMutation } = useCaseMutations();
  const { isUpdating, isWaitingForFollowup, canAnalyze } = useAnalysisAvailability(caseId);
  const runAnalysis = useRunCaseAnalysis(caseId);
  const { analysisResult, sources, overview } = useCaseOverview(caseId);
  const freshness = activeCase?.analysis_freshness ?? "missing";
  const status = isUpdating
    ? "Analyzing…"
    : isWaitingForFollowup
      ? "Waiting for your answer in Ask"
      : freshness === "stale"
        ? "Sources changed since the analysis"
        : freshness === "current"
          ? "Analysis up to date"
          : "Not analyzed yet";
  const statusNeedsAttention =
    !isUpdating && (isWaitingForFollowup || freshness === "stale" || freshness === "missing");
  const analyzeLabel = isUpdating
    ? "Analyzing…"
    : freshness === "current"
      ? "Analyze again"
      : "Analyze";

  const setChatOpen = useCallback((next: boolean) => {
    setIsChatOpen(next);
    try {
      localStorage.setItem(CHAT_OPEN_STORAGE_KEY, String(next));
    } catch (error) {
      console.warn("Could not save the chat panel preference", error);
    }
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

  if (isCaseNotFound(caseQuery.error)) return <CaseNotFound />;

  const flaggedCount = overview.findings.filter(
    (finding) => finding.traceability.semanticSupport === "not_supported",
  ).length;

  return (
    <div className="flex h-dvh overflow-hidden bg-ground text-ink">
      <CaseSidebar
        caseId={caseId}
        caseTitle={activeCase?.title || "New case"}
        compact={isChatOpen}
      />
      <main className="relative flex min-w-0 flex-1 flex-col overflow-y-auto bg-ground">
        <WorkspaceHeader
          activeCase={activeCase}
          activeView={activeView}
          creatingCase={createMutation.isPending}
          status={status}
          statusNeedsAttention={statusNeedsAttention}
          analyzeLabel={analyzeLabel}
          canAnalyze={canAnalyze}
          findingCount={overview.hasAnalysis ? overview.findings.length : 0}
          flaggedCount={flaggedCount}
          sourceCount={sources?.filter((source) => !source.deactivated_at).length}
          analysedAt={analysisResult?.created_at ?? null}
          onAnalyze={
            activeCase
              ? () => {
                  runAnalysis();
                  router.push(casePath(caseId, "analysis"));
                }
              : undefined
          }
          onViewChange={handleViewChange}
          onNewCase={() => void handleNewCase()}
          onRenameCase={(title) => void renameCase(title)}
          isChatOpen={isChatOpen}
          onToggleChat={() => setChatOpen(!isChatOpen)}
          waitingQuestions={isWaitingForFollowup && !isUpdating ? 1 : 0}
        />
        <div className="flex flex-1 flex-col">{children}</div>
      </main>

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
