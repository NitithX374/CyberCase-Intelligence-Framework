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

function pagedDocument(pageCount: number): CaseDocumentRead {
  const pages = Array.from({ length: pageCount }, (_, index) => ({
    page_number: index + 1,
    text: `Page ${index + 1} content`,
    text_method: index % 2 === 0 ? "native" : "ocr",
  }));
  return {
    ...document,
    id: "document-multi",
    filename: "multi-page.pdf",
    extractions: [
      {
        id: "extraction-multi",
        document_id: "document-multi",
        provider: "native_pdf",
        extracted_text: pages.map((page) => page.text).join("\n\n"),
        config_json: {},
        provenance_json: { pages },
        warnings_json: [],
        created_at: "2026-09-11T00:00:00Z",
      },
    ],
  };
}

describe("CaseSourcesView", () => {
  it("switches between a source file and its extracted text", () => {
    renderSources({ documents: [document] });

    expect(screen.getAllByText("statement.pdf")).toHaveLength(2);
    expect(screen.getByRole("tab", { name: "Original" })).toHaveAttribute("aria-selected", "true");
    fireEvent.click(screen.getByRole("tab", { name: "Text" }));
    expect(screen.getByText("Received statement")).toBeInTheDocument();
  });

  it("shows the file size without duplicating source text in the rail", () => {
    renderSources({ documents: [document] });
    expect(screen.getByText("2 KB")).toBeInTheDocument();
    expect(screen.queryByText("Received statement")).not.toBeInTheDocument();
  });

  it("switches the preview when a different source is selected", () => {
    renderSources({ documents: [document, secondDocument] });
    fireEvent.click(screen.getByRole("button", { name: /account-log\.png/i }));
    expect(screen.getByRole("heading", { name: "account-log.png" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("tab", { name: "Text" }));
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
    expect(screen.getByRole("heading", { level: 2, name: "Sources 3" })).toBeInTheDocument();
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
    renderSources({ sources: [caseSource()], onAddNarrative });

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

  it("offers the analysis under the sources until it has read them", () => {
    const onAnalyze = vi.fn();
    renderSources({
      sources: [caseSource()],
      analysis: { freshness: "missing", isRunning: false, onAnalyze },
    });

    fireEvent.click(screen.getByRole("button", { name: "Analyze" }));
    expect(onAnalyze).toHaveBeenCalledOnce();
  });

  it("says when the sources changed since the last analysis", () => {
    renderSources({
      sources: [caseSource()],
      analysis: { freshness: "stale", isRunning: false, onAnalyze: vi.fn() },
    });

    expect(screen.getByText("Sources changed since the last analysis")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze latest" })).toBeEnabled();
  });

  it("keeps the rail clear once the analysis is up to date", () => {
    renderSources({
      sources: [caseSource()],
      analysis: { freshness: "current", isRunning: false, onAnalyze: vi.fn() },
    });

    expect(screen.queryByRole("button", { name: /Analyze/ })).not.toBeInTheDocument();
  });

  it("shows a run in progress instead of a second button", () => {
    renderSources({
      sources: [caseSource()],
      analysis: { freshness: "current", isRunning: true, onAnalyze: vi.fn() },
    });

    expect(screen.getByRole("button", { name: "Analyzing…" })).toBeDisabled();
  });

  it("waits for an upload to finish before analyzing", () => {
    renderSources({
      sources: [caseSource()],
      isUploading: true,
      uploadingFilename: "statement.pdf",
      analysis: { freshness: "missing", isRunning: false, onAnalyze: vi.fn() },
    });

    expect(screen.getByRole("button", { name: "Analyze" })).toBeDisabled();
  });

  it("starts an empty case with a narrative or a file", async () => {
    const onAddNarrative = vi.fn().mockResolvedValue(true);
    renderSources({ onAddNarrative });

    expect(screen.getByRole("heading", { name: "No sources yet" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Upload file" })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Write narrative" }));
    fireEvent.change(screen.getByLabelText("Narrative"), {
      target: { value: "A phishing email reached payroll." },
    });
    fireEvent.click(screen.getByRole("button", { name: "Add narrative" }));
    await waitFor(() =>
      expect(onAddNarrative).toHaveBeenCalledWith({
        title: undefined,
        text: "A phishing email reached payroll.",
      }),
    );
  });

  it("renders one card per extracted page", () => {
    renderSources({ documents: [pagedDocument(2)] });
    fireEvent.click(screen.getByRole("tab", { name: "Text" }));

    expect(screen.getByText("Page 1")).toBeInTheDocument();
    expect(screen.getByText("Page 1 content")).toBeInTheDocument();
    expect(screen.getByText("Page 2")).toBeInTheDocument();
    expect(screen.getByText("Page 2 content")).toBeInTheDocument();
    // Two pages are one scroll; page links would only add noise.
    expect(screen.queryByRole("navigation", { name: "Page navigation" })).not.toBeInTheDocument();
  });

  it("offers page links once a document is long enough to need them", () => {
    renderSources({ documents: [pagedDocument(5)] });
    fireEvent.click(screen.getByRole("tab", { name: "Text" }));

    expect(screen.getByRole("navigation", { name: "Page navigation" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Go to page 1" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Go to page 5" })).toBeInTheDocument();
  });

  it("renders side-by-side comparison view with original file and extracted text", async () => {
    renderSources({ documents: [pagedDocument(2)] });
    fireEvent.click(screen.getByRole("tab", { name: "Side by side" }));

    expect(await screen.findByTitle("Original file: multi-page.pdf")).toBeInTheDocument();
    expect(screen.getByText("Page 1")).toBeInTheDocument();
    expect(screen.getByText("Page 1 content")).toBeInTheDocument();
  });

  it("renders the in-flight pending document item when uploading", () => {
    renderSources({ isUploading: true, uploadingFilename: "forensic_report.pdf" });

    expect(screen.getByText("forensic_report.pdf")).toBeInTheDocument();
    expect(screen.getByText("Extracting text…")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 2, name: "Sources 1" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "No sources yet" })).not.toBeInTheDocument();
  });
});
