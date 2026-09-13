import type { FormEvent } from "react";

import type {
  RunPhase,
  WorkspaceView,
} from "@/components/common/types";
import type {
  ChatMessageAction,
  CaseIntakeSubmission,
  CaseRead,
  CaseAnalysisResultRead,
  CaseClarificationRead,
  CaseDocumentRead,
  CaseEvidenceSnapshotRead,
  CaseRunRead,
  EvidenceSourceRead,
  PersistedChatMessage,
  ThreadStatus,
} from "@/lib/api";

export interface PendingChatSubmission {
  threadId: string;
  caseId: string;
  content: string;
  key: string;
  kind: "message" | "followup";
  action?: ChatMessageAction;
  lastKnownMessageOrdinal: number;
  requestOrdinal?: number;
}

export interface ChatWorkspaceLayoutProps {
  activeCase: CaseRead | null;
  activeCaseId: string | null;
  activeView: WorkspaceView;
  cases: CaseRead[];
  casesLoading: boolean;
  casesError: string | null;
  creatingCase: boolean;
  deletingCaseId: string | null;
  phase: RunPhase;
  threadStatus: ThreadStatus | null;
  queryError: string | null;
  input: string;
  visibleMessages: PersistedChatMessage[];
  messages: PersistedChatMessage[];
  documents: CaseDocumentRead[];
  evidence: EvidenceSourceRead[];
  analysisResult: CaseAnalysisResultRead | null;
  evidenceSnapshot: CaseEvidenceSnapshotRead | null;
  run: CaseRunRead | null;
  runStatus: CaseRunRead["status"] | null;
  clarifications: CaseClarificationRead[];
  analysisLoading: boolean;
  analysisSubmitting: boolean;
  caseDataLoading: boolean;
  snapshotLoading: boolean;
  isUploadingDocument: boolean;
  admittingExtractionId: string | null;
  deleteCandidate: CaseRead | null;
  onSelectCase: (caseId: string) => void;
  onNewCase: () => void;
  onRequestDelete: (caseRecord: CaseRead) => void;
  onViewChange: (view: WorkspaceView) => void;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onSetDeleteCandidate: (caseRecord: CaseRead | null) => void;
  onCancelDelete: () => void;
  onConfirmDelete: () => void;
  onNavigateToSource?: (messageId: string) => void;
  onSubmitCase: (data: CaseIntakeSubmission) => void;
  onClearQueryError: () => void;
  onRetryQuery?: () => void;
  isChatOpen?: boolean;
  onToggleChat?: () => void;
  onUploadDocument: (file: File) => void;
  onAdmitExtraction: (documentId: string, extractionId: string) => void;
}

