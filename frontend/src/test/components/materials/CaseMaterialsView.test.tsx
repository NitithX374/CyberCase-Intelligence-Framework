import { fireEvent, render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";

import { CaseMaterialsView } from "@/components/materials/CaseMaterialsView";
import type { CaseDocumentRead } from "@/lib/api";

vi.mock("@/lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/api")>();
  return {
    ...actual,
    fetchCaseDocumentContent: vi.fn().mockResolvedValue(new Blob(["original"])),
  };
});

const document: CaseDocumentRead = {
  id: "document-1",
  case_id: "case-1",
  filename: "statement.pdf",
  mime_type: "application/pdf",
  size_bytes: 2048,
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

const secondDocument: CaseDocumentRead = {
  ...document,
  id: "document-2",
  filename: "account-log.png",
  mime_type: "image/png",
  extractions: (document.extractions ?? []).map((extraction) => ({
    ...extraction,
    id: "extraction-2",
    document_id: "document-2",
    extracted_text: "Recognized account log",
  })),
};

function renderMaterials(overrides: Partial<React.ComponentProps<typeof CaseMaterialsView>> = {}) {
  const props: React.ComponentProps<typeof CaseMaterialsView> = {
    caseId: "case-1",
    documents: [],
    isUploading: false,
    onUploadDocument: vi.fn(),
    ...overrides,
  };
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(<QueryClientProvider client={queryClient}><CaseMaterialsView {...props} /></QueryClientProvider>);
  return props;
}

  describe("CaseMaterialsView", () => {
  it("switches between a source file and its System OCR output", () => {
    renderMaterials({ documents: [document] });

    expect(screen.getAllByText("statement.pdf")).toHaveLength(2);
    expect(screen.getByRole("tab", { name: "Original File" })).toHaveAttribute("aria-selected", "true");
    fireEvent.click(screen.getByRole("tab", { name: "System OCR" }));
    expect(screen.getByText("Received statement")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Admit OCR" })).not.toBeInTheDocument();
  });

  it("shows the received state without duplicating evidence text in the source rail", () => {
    renderMaterials({ documents: [document] });
    expect(screen.getByText("Received")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Admit OCR" })).not.toBeInTheDocument();
  });

  it("switches the preview when a different source is selected", () => {
    renderMaterials({ documents: [document, secondDocument] });
    fireEvent.click(screen.getByRole("button", { name: /account-log\.png/i }));
    expect(screen.getByRole("heading", { name: "account-log.png" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", { name: "System OCR" }));
    expect(screen.getByText("Recognized account log")).toBeInTheDocument();
  });

  it("renders the canonical empty Case state", () => {
    renderMaterials();
    expect(screen.getByText("No source files yet.")).toBeInTheDocument();
    expect(screen.getByText("Add a source file to begin reviewing materials.")).toBeInTheDocument();
  });
});
