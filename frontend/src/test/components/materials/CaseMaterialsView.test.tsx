import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
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
    exact_text: "Admitted case narrative",
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
  size_bytes: 2048,
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

function renderMaterials(overrides: Partial<React.ComponentProps<typeof CaseMaterialsView>> = {}) {
  const props: React.ComponentProps<typeof CaseMaterialsView> = {
    documents: [],
    evidence: [],
    isUploading: false,
    admittingExtractionId: null,
    onUploadDocument: vi.fn(),
    onAdmitExtraction: vi.fn(),
    ...overrides,
  };
  render(<CaseMaterialsView {...props} />);
  return props;
}

describe("CaseMaterialsView", () => {
  it("renders saved documents and admitted evidence from Case-owned state", () => {
    const onAdmitExtraction = vi.fn();
    renderMaterials({ documents: [document], evidence: [evidence], onAdmitExtraction });

    expect(screen.getByText("statement.pdf")).toBeInTheDocument();
    expect(screen.getByText("Admitted case narrative")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Admit reviewed text" }));
    expect(onAdmitExtraction).toHaveBeenCalledWith("document-1", "extraction-1");
  });

  it("renders the canonical empty Case state", () => {
    renderMaterials();
    expect(screen.getByText("No case material has been saved yet.")).toBeInTheDocument();
  });
});
