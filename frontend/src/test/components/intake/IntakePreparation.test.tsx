import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CaseIntakeView } from "@/components/intake/CaseIntakeView";
import type { CaseDocumentRead, EvidenceSourceRead } from "@/lib/api";

const evidence: EvidenceSourceRead = {
  id: "source-1",
  case_id: "case-1",
  source_kind: "narrative",
  document_id: null,
  origin_message_id: null,
  exact_text: "Received case material",
  source_metadata_json: {},
  created_at: "2026-09-11T00:00:00Z",
  archived_at: null,
};

const document: CaseDocumentRead = {
  id: "document-1",
  case_id: "case-1",
  filename: "statement.pdf",
  mime_type: "application/pdf",
  size_bytes: 1024,
  created_at: "2026-09-11T00:00:00Z",
  archived_at: null,
  extractions: [{
    id: "extraction-1",
    document_id: "document-1",
    provider: "native_pdf",
    extracted_text: "Received statement",
    config_json: {},
    provenance_json: {},
    warnings_json: [],
    created_at: "2026-09-11T00:00:00Z",
  }],
};

function renderIntake(overrides: Partial<React.ComponentProps<typeof CaseIntakeView>> = {}) {
  const props: React.ComponentProps<typeof CaseIntakeView> = {
    caseId: "case-1",
    documents: [],
    evidence: [],
    analysisResult: null,
    run: null,
    isSubmitting: false,
    isCaseDataLoading: false,
    isUploadingDocument: false,
    onSubmitCase: vi.fn(),
    onUploadDocument: vi.fn(),
    ...overrides,
  };
  render(<CaseIntakeView {...props} />);
  return props;
}

describe("Case preparation workflow", () => {
  it("starts native analysis from received Case evidence without another narrative", () => {
    const onSubmitCase = vi.fn();
    renderIntake({ evidence: [evidence], onSubmitCase });

    const analyzeButton = screen.getByRole("button", { name: /Analyze case/i });
    expect(analyzeButton).not.toBeDisabled();
    fireEvent.click(analyzeButton);
    expect(onSubmitCase).toHaveBeenCalledWith({ title: undefined, description: "" });
  });

  it("keeps analysis disabled while Case material is loading", () => {
    renderIntake({ isCaseDataLoading: true });

    expect(screen.getByRole("status")).toHaveTextContent("Loading case material");
    expect(screen.getByRole("button", { name: /Analyze case/i })).toBeDisabled();
  });

  it("receives Case documents after upload without a separate admission action", () => {
    const onUploadDocument = vi.fn();
    renderIntake({ documents: [document], onUploadDocument });

    const file = new File(["pdf"], "new.pdf", { type: "application/pdf" });
    fireEvent.change(screen.getByLabelText("Add files"), { target: { files: [file] } });

    expect(onUploadDocument).toHaveBeenCalledWith(file);
    expect(screen.getByText("Received")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Admit text" })).not.toBeInTheDocument();
  });
});
