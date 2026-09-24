import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { CaseAnalysisResultRead, CaseSourceRead, ChatMessageRead } from "@/lib/api";
import { mockNativeDialog } from "@/test/mockNativeDialog";
import CaseAnalysisPage from "./page";

mockNativeDialog();

const caseId = "22222222-2222-4222-8222-222222222222";
const answer = "The attacker came in through the web server.";

const narrative: CaseSourceRead = {
  id: "11111111-1111-4111-8111-111111111111",
  case_id: caseId,
  source_kind: "narrative",
  document_id: null,
  exact_text: "Payroll files were encrypted overnight.",
  provenance_json: {},
  source_metadata_json: {},
  created_at: "2026-09-10T00:00:00Z",
  archived_at: null,
};

const messages: ChatMessageRead[] = [
  {
    id: "question-1",
    case_id: caseId,
    ordinal: 1,
    role: "assistant",
    content: "How did the attacker get in?",
    message_kind: "followup_question",
    gap_key: "topic:initial-access",
    analysis_result_id: null,
    metadata_json: {},
    created_at: "2026-09-10T00:01:00Z",
  },
  {
    id: "answer-1",
    case_id: caseId,
    ordinal: 2,
    role: "user",
    content: answer,
    message_kind: "followup_answer",
    analysis_result_id: null,
    in_reply_to_message_id: "question-1",
    metadata_json: {},
    created_at: "2026-09-10T00:02:00Z",
  },
];

const analysis: CaseAnalysisResultRead = {
  id: "44444444-4444-4444-8444-444444444444",
  case_id: caseId,
  source_revision: 1,
  schema_version: "case_analysis_trace_v1",
  status: "validated",
  summary: answer,
  trace_json: {
    version: "case_analysis_trace_v1",
    validation_status: "validated",
    analysis_mode: "case_overview",
    summary: answer,
    claims: [
      {
        claim_id: "A-01",
        claim_type: "reported",
        text: answer,
        epistemic_status: "reported",
        reasoning_summary: null,
        supporting_source_ids: ["QA-01"],
        contradicting_source_ids: [],
        supporting_citations: [{ source_id: "QA-01", exact_quote: answer }],
        contradicting_citations: [],
      },
    ],
    gaps: [],
    mitre_associations: [
      {
        association_id: "MA-01",
        technique_id: "T1190",
        claim_ids: ["A-01"],
        reason: "The answer describes entry through a public web server.",
        plain_meaning: "The attacker used a flaw in a public-facing application.",
        status: "candidate_only",
        support_role: "external_technical_context",
      },
    ],
    retrieval_context_id: "retrieval-1",
  },
  retrieval_context_id: "retrieval-1",
  pipeline_config: {},
  external_context_json: {
    technical_augmentation: {
      version: "case_mitre_augmentation_v1",
      status: "retrieved_with_matches",
      retrieval_context_id: "retrieval-1",
      mitre_table: [
        {
          technique_id: "T1190",
          name: "Exploit Public-Facing Application",
          tactic: "Initial Access",
          description: "Adversaries may exploit a public-facing application.",
        },
      ],
      association_ids: ["MA-01"],
    },
  },
  created_at: "2026-09-10T12:00:00Z",
  freshness: "current",
};

vi.mock("next/navigation", () => ({
  useParams: () => ({ caseId }),
  useRouter: () => ({ push: vi.fn() }),
}));
vi.mock("@/features/cases/queries", () => ({
  useCase: () => ({ data: { id: caseId, title: "Encrypted payroll" } }),
}));
vi.mock("@/features/analysis/queries", () => ({
  useCaseAnalysis: () => ({ data: analysis, isLoading: false }),
}));
vi.mock("@/features/sources/queries", () => ({
  useCaseSources: () => ({ data: [narrative], isLoading: false }),
}));
vi.mock("@/features/chat/useCaseChat", () => ({
  useCaseChatMessages: () => ({ data: { case_id: caseId, messages }, isLoading: false }),
}));
vi.mock("@/features/analysis/CaseOverviewView", () => ({ CaseOverviewView: () => null }));
vi.mock("@/features/reports/CaseReportView", () => ({ CaseReportView: () => null }));

describe("CaseAnalysisPage", () => {
  it("shows ATT&CK context that rests on a follow-up answer", () => {
    render(<CaseAnalysisPage />);

    expect(
      screen.getByRole("heading", { name: "Exploit Public-Facing Application" }),
    ).toBeInTheDocument();
    expect(screen.queryByText(/could not be verified/)).not.toBeInTheDocument();
  });
});
