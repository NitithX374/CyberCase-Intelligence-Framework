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
  chatThreadId,
  activeView,
  activeWorkspaceView,
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
  nativeDocuments,
  nativeEvidence,
  nativeAnalysisResult,
  nativeEvidenceSnapshot,
  nativeRun,
  nativeRunStatus,
  nativeClarifications,
  clarificationSubmittingId = null,
  nativeAnalysisLoading = false,
  nativeAnalysisSubmitting = false,
  nativeCaseDataLoading = false,
  nativeSnapshotLoading = false,
  nativeIsUploadingDocument = false,
  nativeAdmittingExtractionId = null,
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
  onUploadNativeDocument,
  onAdmitNativeExtraction,
  onAnswerClarification,
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
    <div className="flex h-dvh overflow-hidden bg-canvas text-ink">
      {/* 1. Left Sidebar Navigation */}
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

      {/* 2. Middle Work Area (WorkspaceHeader on top, Document view scrollable below) */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
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

        <main className="flex min-w-0 flex-1 flex-col overflow-y-auto bg-canvas">
          {activeWorkspaceView === "intake" ? (
            <CaseIntakeView
              caseKey={activeCaseId ?? "draft"}
              threadId={chatThreadId}
              threadStatus={threadStatus}
              isSubmitting={nativeAnalysisSubmitting || phase === "querying" || phase === "analyzing"}
              error={queryError ?? (nativeRun?.status === "failed" ? (nativeRun.error_message || "The case analysis failed.") : null)}
              nativeCaseDataLoading={nativeCaseDataLoading}
              onSubmitCase={onSubmitCase}
              messages={messages}
              nativeCaseId={activeCaseId ?? undefined}
              nativeDocuments={nativeDocuments ?? []}
              nativeEvidence={nativeEvidence ?? []}
              nativeAnalysisResult={nativeAnalysisResult}
              nativeRun={nativeRun}
              nativeIsUploadingDocument={nativeIsUploadingDocument}
              nativeAdmittingExtractionId={nativeAdmittingExtractionId}
              onUploadNativeDocument={onUploadNativeDocument}
              onAdmitNativeExtraction={onAdmitNativeExtraction}
              onOpenOverview={() => onViewChange("overview")}
              onOpenChat={handleOpenChat}
              onOpenMaterials={() => onViewChange("materials")}
            />
          ) : activeWorkspaceView === "overview" ? (
            <CaseOverviewView
              threadId={activeCaseId}
              threadTitle={displayCaseTitle}
              threadStatus={threadStatus ?? "idle"}
              messages={messages}
              nativeAnalysisResult={nativeAnalysisResult}
              nativeEvidenceSnapshot={nativeEvidenceSnapshot}
              nativeRunStatus={nativeRunStatus}
              nativeRun={nativeRun}
              nativeClarifications={nativeClarifications}
              clarificationSubmittingId={clarificationSubmittingId}
              onAnswerClarification={onAnswerClarification}
              nativeAnalysisLoading={nativeAnalysisLoading}
              nativeSnapshotLoading={nativeSnapshotLoading}
              onOpenChat={handleOpenChat}
              onOpenReport={() => onViewChange("report")}
              onOpenIntake={() => onViewChange("intake")}
              onOpenMaterials={() => onViewChange("materials")}
              onOpenTechnicalContext={() => onViewChange("technical-context")}
              onNavigateToSource={onNavigateToSource}
              onRunAnalysis={() => onSubmitCase({ title: undefined, description: "" })}
            />
          ) : activeWorkspaceView === "materials" ? (
            <CaseMaterialsView
              messages={messages}
              nativeDocuments={nativeDocuments ?? []}
              nativeEvidence={nativeEvidence ?? []}
              isUploadingDocument={nativeIsUploadingDocument}
              admittingExtractionId={nativeAdmittingExtractionId}
              onUploadDocument={onUploadNativeDocument}
              onAdmitExtraction={onAdmitNativeExtraction}
              onOpenChat={handleOpenChat}
              onOpenIntake={() => onViewChange("intake")}
            />
          ) : activeWorkspaceView === "technical-context" ? (
            <TechnicalContextView
              messages={messages}
              nativeAnalysisResult={nativeAnalysisResult}
              nativeEvidenceSnapshot={nativeEvidenceSnapshot}
              onOpenIntake={() => onViewChange("intake")}
              onNavigateToSource={onNavigateToSource}
            />
          ) : (
            activeCaseId ? (
              <CaseReportView
                key={`${activeCaseId}:${nativeAnalysisResult?.id ?? "empty"}`}
                caseId={activeCaseId}
                caseTitle={displayCaseTitle}
                analysisResult={nativeAnalysisResult ?? null}
                runStatus={nativeRunStatus ?? null}
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
        hasAnalysisContext={nativeAnalysisResult?.status === "validated"}
        leadResult={nativeAnalysisResult}
        leadSnapshot={nativeEvidenceSnapshot}
        onViewChange={onViewChange}
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
        onClose={onClearQueryError ?? (() => { })}
        onRetry={onRetryQuery}
      />
    </div>
  );
}

function ReportEmptyState() {
  return (
    <section className="mx-auto flex w-full max-w-3xl flex-1 items-center justify-center px-6 py-12">
      <div className="rounded-2xl border border-line bg-panel px-6 py-8 text-center shadow-sm">
        <h1 className="text-lg font-semibold text-ink">Select a Case to view its report</h1>
        <p className="mt-2 text-sm text-muted">Reports are generated from a persisted Case analysis.</p>
      </div>
    </section>
  );
}
