"use client";

import { CaseOverviewView } from "@/components/overview/CaseOverviewView";
import { CaseIntakeView } from "@/components/intake/CaseIntakeView";
import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
import { TechnicalContextView } from "@/components/technical/TechnicalContextView";
import { CaseReportView } from "@/components/report/CaseReportView";
import { WorkspaceChatPanel } from "@/components/conversation/WorkspaceChatPanel";
import { DeleteCaseDialog } from "@/components/common/DeleteDialog";
import { MeaningfulErrorModal } from "@/components/common/MeaningfulErrorModal";
import { toUserFacingError } from "@/lib/user-facing-error";
import { WorkspaceSidebar } from "@/components/layout/WorkspaceSidebar";
import { WorkspaceHeader } from "@/components/layout/WorkspaceHeader";
import type { ChatWorkspaceLayoutProps } from "@/features/chat/workspace/chat-workspace-types";

export function ChatWorkspaceLayout({
  activeCase,
  activeCaseId,
  activeView,
  cases,
  casesLoading,
  casesError,
  creatingCase,
  deletingCaseId,
  phase,
  threadStatus,
  queryError,
  input,
  visibleMessages,
  messages,
  documents,
  evidence,
  analysisResult,
  evidenceSnapshot,
  run,
  runStatus,
  clarifications,
  analysisLoading,
  analysisSubmitting,
  caseDataLoading,
  snapshotLoading,
  isUploadingDocument,
  admittingExtractionId,
  deleteCandidate,
  onSelectCase,
  onNewCase,
  onRequestDelete,
  onViewChange,
  onInputChange,
  onSubmit,
  onSetDeleteCandidate,
  onCancelDelete,
  onConfirmDelete,
  onNavigateToSource,
  onSubmitCase,
  onClearQueryError,
  onRetryQuery,
  isChatOpen = true,
  onToggleChat,
  onUploadDocument,
  onAdmitExtraction,
}: ChatWorkspaceLayoutProps) {
  const displayCaseTitle =
    !activeCase?.title
      ? "New case"
      : activeCase.title;

  const handleOpenChat = () => {
    if (!isChatOpen && onToggleChat) {
      onToggleChat();
    }
  };

  return (
    <div className="flex h-dvh overflow-hidden bg-surface text-ink">
      <WorkspaceSidebar
        cases={cases}
        activeCaseId={activeCaseId}
        casesLoading={casesLoading}
        casesError={casesError}
        onSelectCase={onSelectCase}
        onNewCase={onNewCase}
        onRequestDelete={onRequestDelete}
        deletingCaseId={deletingCaseId}
        activeView={activeView}
        onViewChange={onViewChange}
      />

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden bg-surface">
        <WorkspaceHeader
          activeCase={activeCase}
          activeCaseId={activeCaseId}
          activeView={activeView}
          cases={cases}
          creatingCase={creatingCase}
          deletingCaseId={deletingCaseId}
          phase={phase}
          onViewChange={onViewChange}
          onSelectCase={onSelectCase}
          onNewCase={onNewCase}
          onRequestDelete={onSetDeleteCandidate}
          isChatOpen={isChatOpen}
          onToggleChat={onToggleChat}
        />

        <main className="flex min-w-0 flex-1 flex-col overflow-y-auto bg-surface">
          {activeView === "intake" ? activeCaseId ? (
            <CaseIntakeView
              caseId={activeCaseId}
              isSubmitting={analysisSubmitting || phase === "querying" || phase === "analyzing"}
              error={queryError ?? (run?.status === "failed" ? (run.error_message || "The case analysis failed.") : null)}
              isCaseDataLoading={caseDataLoading}
              onSubmitCase={onSubmitCase}
              documents={documents}
              evidence={evidence}
              analysisResult={analysisResult}
              run={run}
              isUploadingDocument={isUploadingDocument}
              admittingExtractionId={admittingExtractionId}
              onUploadDocument={onUploadDocument}
              onAdmitExtraction={onAdmitExtraction}
              onOpenOverview={() => onViewChange("overview")}
              onOpenChat={handleOpenChat}
              onOpenMaterials={() => onViewChange("materials")}
            />
          ) : null : activeView === "overview" ? (
            <CaseOverviewView
              threadId={activeCaseId}
              threadTitle={displayCaseTitle}
              threadStatus={threadStatus ?? "idle"}
              analysisResult={analysisResult}
              evidenceSnapshot={evidenceSnapshot}
              runStatus={runStatus}
              run={run}
              clarifications={clarifications}
              analysisLoading={analysisLoading}
              snapshotLoading={snapshotLoading}
              onOpenChat={handleOpenChat}
              onOpenReport={() => onViewChange("report")}
              onOpenIntake={() => onViewChange("intake")}
              onOpenMaterials={() => onViewChange("materials")}
              onOpenTechnicalContext={() => onViewChange("technical-context")}
              onNavigateToSource={onNavigateToSource}
              onRunAnalysis={() => onSubmitCase({ title: undefined, description: "" })}
            />
          ) : activeView === "materials" ? (
            <CaseMaterialsView
              caseId={activeCaseId ?? ""}
              documents={documents}
              evidence={evidence}
              isUploading={isUploadingDocument}
              admittingExtractionId={admittingExtractionId}
              onUploadDocument={onUploadDocument}
              onAdmitExtraction={onAdmitExtraction}
              onOpenChat={handleOpenChat}
              onOpenIntake={() => onViewChange("intake")}
            />
          ) : activeView === "technical-context" ? (
            <TechnicalContextView
              analysisResult={analysisResult}
              evidenceSnapshot={evidenceSnapshot}
              onOpenIntake={() => onViewChange("intake")}
              onNavigateToSource={onNavigateToSource}
            />
          ) : (
            activeCaseId ? (
              <CaseReportView
                key={`${activeCaseId}:${analysisResult?.id ?? "empty"}`}
                caseId={activeCaseId}
                caseTitle={displayCaseTitle}
                analysisResult={analysisResult}
                runStatus={runStatus}
                onOpenChat={handleOpenChat}
                onOpenOverview={() => onViewChange("overview")}
              />
            ) : (
              <ReportEmptyState />
            )
          )}
        </main>
      </div>

      <WorkspaceChatPanel
        isOpen={isChatOpen}
        phase={phase}
        messages={messages}
        visibleMessages={visibleMessages}
        threadStatus={threadStatus}
        input={input}
        hasAnalysisContext={analysisResult?.status === "validated"}
        leadResult={analysisResult}
        leadSnapshot={evidenceSnapshot}
        onViewChange={onViewChange}
        onNavigateToSource={onNavigateToSource}
        onInputChange={onInputChange}
        onSubmit={onSubmit}
        onToggleChat={onToggleChat}
      />

      <DeleteCaseDialog
        caseRecord={deleteCandidate}
        isDeleting={deletingCaseId !== null}
        onCancel={onCancelDelete}
        onConfirm={onConfirmDelete}
      />
      <MeaningfulErrorModal
        isOpen={Boolean(queryError)}
        error={
          queryError
            ? toUserFacingError(queryError, {
              isUncertain: phase === "querying" || phase === "analyzing",
            })
            : null
        }
        onClose={onClearQueryError}
        onRetry={onRetryQuery}
      />
    </div>
  );
}

function ReportEmptyState() {
  return (
    <section className="mx-auto flex w-full max-w-3xl flex-1 items-center justify-center px-6 py-12">
      <div className="border-y border-line px-6 py-8 text-center">
        <h1 className="text-lg font-semibold text-ink">Select a Case to view its report</h1>
        <p className="mt-2 text-sm text-ink-muted">Reports are generated from a persisted Case analysis.</p>
      </div>
    </section>
  );
}
