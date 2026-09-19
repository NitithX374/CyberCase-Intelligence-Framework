import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";

import { CaseSourcesView } from "@/components/sources/CaseSourcesView";
import type { CaseDocumentRead, CaseSourceRead } from "@/lib/api";

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
  extractions: [
    {
      id: "extraction-1",
      document_id: "document-1",
      provider: "native_pdf",
      extracted_text: "Received statement",
      config_json: {},
      provenance_json: {},
      warnings_json: [],
      created_at: "2026-09-11T00:00:00Z",
    },
  ],
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

function caseSource(overrides: Partial<CaseSourceRead> = {}): CaseSourceRead {
  return {
    id: "source-1",
    case_id: "case-1",
    source_kind: "narrative",
    document_id: null,
    origin_message_id: null,
    exact_text: "Files on the shared drive were reported encrypted.",
    provenance_json: {},
    source_metadata_json: {},
    created_at: "2026-09-11T00:00:00Z",
    archived_at: null,
    ...overrides,
  };
}

function renderSources(overrides: Partial<React.ComponentProps<typeof CaseSourcesView>> = {}) {
  const props: React.ComponentProps<typeof CaseSourcesView> = {
    caseId: "case-1",
    documents: [],
    sources: [],
    isUploading: false,
    isAddingNarrative: false,
    onUploadDocument: vi.fn(),
    onAddNarrative: vi.fn().mockResolvedValue(true),
    ...overrides,
  };
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={queryClient}>
      <CaseSourcesView {...props} />
    </QueryClientProvider>,
  );
  return props;
}

describe("CaseSourcesView", () => {
  it("switches between a source file and its System OCR output", () => {
    renderSources({ documents: [document] });

    expect(screen.getAllByText("statement.pdf")).toHaveLength(2);
    expect(screen.getByRole("tab", { name: "Original File" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    fireEvent.click(screen.getByRole("tab", { name: "System OCR" }));
    expect(screen.getByText("Received statement")).toBeInTheDocument();
  });

  it("shows the received state without duplicating source text in the rail", () => {
    renderSources({ documents: [document] });
    expect(screen.getByText("2 KB · Received")).toBeInTheDocument();
  });

  it("switches the preview when a different source is selected", () => {
    renderSources({ documents: [document, secondDocument] });
    fireEvent.click(screen.getByRole("button", { name: /account-log\.png/i }));
    expect(screen.getByRole("heading", { name: "account-log.png" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", { name: "System OCR" }));
    expect(screen.getByText("Recognized account log")).toBeInTheDocument();
  });

  it("lists files, narratives and follow-up answers together", () => {
    renderSources({
      documents: [document],
      sources: [
        caseSource(),
        caseSource({
          id: "source-2",
          source_kind: "followup_answer",
          exact_text: "The backups were offline.",
        }),
      ],
    });

    expect(screen.getByRole("heading", { level: 3, name: "Files" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 3, name: "Case narrative" })).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 3, name: "Follow-up answers" }),
    ).toBeInTheDocument();
    expect(screen.getByText("3 sources")).toBeInTheDocument();
  });

  it("reads a follow-up answer in the preview", () => {
    renderSources({
      sources: [
        caseSource({
          id: "source-2",
          source_kind: "followup_answer",
          exact_text: "The backups were offline.",
        }),
      ],
    });

    expect(screen.getByText("Follow-up answer")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "The backups were offline." })).toBeInTheDocument();
    // The rail label, the preview heading, and the text being read.
    expect(screen.getAllByText("The backups were offline.")).toHaveLength(3);
  });

  it("adds a case narrative from the plus menu", async () => {
    const onAddNarrative = vi.fn().mockResolvedValue(true);
    renderSources({ onAddNarrative });

    fireEvent.click(screen.getByRole("button", { name: "Add source" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Case narrative" }));

    fireEvent.change(screen.getByLabelText(/Case title/i), {
      target: { value: "Ransomware on the file server" },
    });
    fireEvent.change(screen.getByLabelText("Narrative"), {
      target: { value: "Files were encrypted overnight." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Add narrative" }));

    await waitFor(() =>
      expect(onAddNarrative).toHaveBeenCalledWith({
        title: "Ransomware on the file server",
        text: "Files were encrypted overnight.",
      }),
    );
  });

  it("leaves running the analysis to the header", () => {
    renderSources({ sources: [caseSource()] });
    expect(screen.queryByRole("button", { name: /Analyze/ })).not.toBeInTheDocument();
  });

  it("renders the canonical empty Case state", () => {
    renderSources();
    expect(screen.getByText("Nothing yet. Add a case narrative or a file.")).toBeInTheDocument();
    expect(screen.getByText("This case has no sources yet.")).toBeInTheDocument();
  });

  it("renders page cards and jump links for multi-page extraction", () => {
    const multiPageDocument: CaseDocumentRead = {
      ...document,
      id: "document-multi",
      filename: "multi-page.pdf",
      extractions: [
        {
          id: "extraction-multi",
          document_id: "document-multi",
          provider: "native_pdf",
          extracted_text: "First page content\n\nSecond page content",
          config_json: {},
          provenance_json: {
            pages: [
              { page_number: 1, text: "First page content", text_method: "native" },
              { page_number: 2, text: "Second page content", text_method: "ocr" },
            ],
          },
          warnings_json: [],
          created_at: "2026-09-11T00:00:00Z",
        },
      ],
    };

    renderSources({ documents: [multiPageDocument] });
    fireEvent.click(screen.getByRole("tab", { name: "System OCR" }));

    expect(screen.getByText("Page 1")).toBeInTheDocument();
    expect(screen.getByText("First page content")).toBeInTheDocument();
    expect(screen.getByText("Page 2")).toBeInTheDocument();
    expect(screen.getByText("Second page content")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Page navigation" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "P.1" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "P.2" })).toBeInTheDocument();
  });

  it("renders side-by-side comparison view with original file and OCR", async () => {
    const multiPageDocument: CaseDocumentRead = {
      ...document,
      id: "document-multi",
      filename: "multi-page.pdf",
      extractions: [
        {
          id: "extraction-multi",
          document_id: "document-multi",
          provider: "native_pdf",
          extracted_text: "First page content\n\nSecond page content",
          config_json: {},
          provenance_json: {
            pages: [
              { page_number: 1, text: "First page content", text_method: "native" },
              { page_number: 2, text: "Second page content", text_method: "ocr" },
            ],
          },
          warnings_json: [],
          created_at: "2026-09-11T00:00:00Z",
        },
      ],
    };

    renderSources({ documents: [multiPageDocument] });
    fireEvent.click(screen.getByRole("tab", { name: "Side by Side" }));

    expect(await screen.findByTitle("Original file: multi-page.pdf")).toBeInTheDocument();
    expect(screen.getByText("Page 1")).toBeInTheDocument();
    expect(screen.getByText("First page content")).toBeInTheDocument();
  });

  it("renders the in-flight pending document item when uploading", () => {
    renderSources({ isUploading: true, uploadingFilename: "forensic_report.pdf" });

    expect(screen.getByText("forensic_report.pdf")).toBeInTheDocument();
    expect(screen.getByText("Extracting text…")).toBeInTheDocument();
    expect(screen.getByText("1 source")).toBeInTheDocument();
    expect(
      screen.queryByText("Nothing yet. Add a case narrative or a file."),
    ).not.toBeInTheDocument();
  });
});
