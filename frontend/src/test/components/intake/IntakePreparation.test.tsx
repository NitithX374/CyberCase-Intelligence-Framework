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
  source_metadata_json: {},
  created_at: "2026-09-11T00:00:00Z",
  archived_at: null,
  revisions: [{
    id: "revision-1",
    source_id: "source-1",
    revision: 1,
    exact_text: "Admitted case material",
    text_sha256: "hash",
    provenance_json: {},
    extraction_id: null,
    admitted_at: "2026-09-11T00:00:00Z",
    archived_at: null,
  }],
};

const document: CaseDocumentRead = {
  id: "document-1",
  case_id: "case-1",
  filename: "statement.pdf",
  mime_type: "application/pdf",
  size_bytes: 1024,
  content_sha256: "hash",
  created_at: "2026-09-11T00:00:00Z",
  archived_at: null,
  extractions: [{
    id: "extraction-1",
    document_id: "document-1",
    revision: 1,
    provider: "native_pdf",
    extracted_text: "Reviewed statement",
    text_sha256: "hash",
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
    admittingExtractionId: null,
    onSubmitCase: vi.fn(),
    onUploadDocument: vi.fn(),
    onAdmitExtraction: vi.fn(),
    ...overrides,
  };
  render(<CaseIntakeView {...props} />);
  return props;
}

describe("Case preparation workflow", () => {
  it("starts native analysis from admitted Case evidence without another narrative", () => {
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

  it("uses Case document upload and explicit extraction admission actions", () => {
    const onUploadDocument = vi.fn();
    const onAdmitExtraction = vi.fn();
    renderIntake({ documents: [document], onUploadDocument, onAdmitExtraction });

    const file = new File(["pdf"], "new.pdf", { type: "application/pdf" });
    fireEvent.change(screen.getByLabelText("Add files"), { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: "Admit text" }));

    expect(onUploadDocument).toHaveBeenCalledWith(file);
    expect(onAdmitExtraction).toHaveBeenCalledWith("document-1", "extraction-1");
  });
});
