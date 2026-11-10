import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";

import { CaseSourcesView } from "@/features/sources/CaseSourcesView";
import type { CaseSourceRead } from "@/lib/api/types";

vi.mock("@/features/sources/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/features/sources/api")>();
  return {
    ...actual,
    fetchCaseDocumentContent: vi.fn().mockResolvedValue(new Blob(["original"])),
  };
});

interface DocumentFacts {
  id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
}

const document: DocumentFacts = {
  id: "document-1",
  filename: "statement.pdf",
  mime_type: "application/pdf",
  size_bytes: 2048,
};

const secondDocument: DocumentFacts = {
  ...document,
  id: "document-2",
  filename: "account-log.png",
  mime_type: "image/png",
};

function documentSource(
  owner: DocumentFacts,
  text: string,
  provenance: Record<string, unknown> = {},
): CaseSourceRead {
  return caseSource({
    id: `source-${owner.id}`,
    source_kind: "document",
    document_id: owner.id,
    filename: owner.filename,
    mime_type: owner.mime_type,
    size_bytes: owner.size_bytes,
    exact_text: text,
    provenance_json: provenance,
  });
}

const statement = {
  sources: [documentSource(document, "Received statement")],
};

function caseSource(overrides: Partial<CaseSourceRead> = {}): CaseSourceRead {
  return {
    id: "source-1",
    case_id: "case-1",
    source_kind: "narrative",
    document_id: null,
    exact_text: "Files on the shared drive were reported encrypted.",
    provenance_json: {},
    source_metadata_json: {},
    created_at: "2026-09-11T00:00:00Z",
    ...overrides,
  };
}

function renderSources(overrides: Partial<React.ComponentProps<typeof CaseSourcesView>> = {}) {
  const props: React.ComponentProps<typeof CaseSourcesView> = {
    caseId: "case-1",
    sources: [],
    followups: [],
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

function pagedDocument(pageCount: number) {
  const pages = Array.from({ length: pageCount }, (_, index) => ({
    page_number: index + 1,
    text: `Page ${index + 1} content`,
    text_method: index % 2 === 0 ? "native" : "ocr",
  }));
  const paged: DocumentFacts = { ...document, id: "document-multi", filename: "multi-page.pdf" };
  const text = pages.map((page) => page.text).join("\n\n");
  return { sources: [documentSource(paged, text, { pages })] };
}

describe("CaseSourcesView", () => {
  it("switches between a source file and its extracted text", () => {
    renderSources(statement);

    expect(screen.getAllByText("statement.pdf")).toHaveLength(2);
    expect(screen.getByRole("button", { name: "Original" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    fireEvent.click(screen.getByRole("button", { name: "Text" }));
    expect(screen.getByText("Received statement")).toBeInTheDocument();
  });

  it("shows the file size without duplicating source text in the rail", () => {
    renderSources(statement);
    expect(screen.getByText("PDF · 1 page · 2 KB")).toBeInTheDocument();
    expect(screen.queryByText("Received statement")).not.toBeInTheDocument();
  });

  it("reads the file's name, type and size from its source, with no document list", () => {
    renderSources(statement);
    expect(screen.getByRole("heading", { level: 2, name: "statement.pdf" })).toBeInTheDocument();
    expect(screen.getByText("PDF · 1 page")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^statement\.pdf/ })).toHaveTextContent(
      "PDF · 1 page · 2 KB",
    );
  });

  it("says a file read by OCR was read by OCR instead of giving its size", () => {
    renderSources({
      sources: [
        documentSource(document, "Received statement", {
          extraction_method: "document_recognition",
          verification_status: "machine_read",
          pages: [
            {
              page_number: 1,
              text: "Received statement",
              text_method: "ocr",
              verification_status: "machine_read",
            },
          ],
        }),
      ],
    });

    expect(screen.getByRole("button", { name: /^statement\.pdf/ })).toHaveTextContent(
      "PDF · 1 page · read by OCR",
    );
  });

  it("calls a narrative typed and counts the sources used", () => {
    renderSources({
      sources: [
        caseSource(),
        caseSource({
          id: "source-2",
          exact_text: "The help desk logged a call.",
          deactivated_at: "2026-10-17T02:00:00Z",
        }),
      ],
      onSetSourceActive: vi.fn().mockResolvedValue(undefined),
    });

    expect(screen.getByRole("button", { name: /^Files on the shared drive/ })).toHaveTextContent(
      /Typed · /,
    );
    expect(screen.getByRole("button", { name: /^The help desk/ })).toHaveTextContent(
      /Not used · Typed · /,
    );
    expect(screen.getByRole("heading", { level: 2, name: /1 of 2 used/ })).toBeInTheDocument();
    expect(
      screen.getByText(
        "Ticked sources go into the next analysis. Changing a tick makes the current analysis out of date.",
      ),
    ).toBeInTheDocument();
  });

  it("counts the warnings recorded when the file was read", () => {
    renderSources({
      sources: [
        documentSource(document, "Received statement", {
          warnings: ["Page 1: recognition confidence was low."],
        }),
      ],
    });
    fireEvent.click(screen.getByRole("button", { name: "Text" }));
    expect(screen.getByText("1 extraction warning")).toBeInTheDocument();
  });

  it("switches the preview when a different source is selected", () => {
    renderSources({
      sources: [
        documentSource(document, "Received statement"),
        documentSource(secondDocument, "Recognized account log"),
      ],
    });
    fireEvent.click(screen.getByRole("button", { name: /account-log\.png/i }));
    expect(screen.getByRole("heading", { name: "account-log.png" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Text" }));
    expect(screen.getByText("Recognized account log")).toBeInTheDocument();
  });

  it("lists files, narratives and follow-up answers together", () => {
    renderSources({
      sources: [documentSource(document, "Received statement"), caseSource()],
      followups: [
        { qaId: "QA-01", question: "Were backups kept?", answer: "The backups were offline." },
      ],
    });

    expect(screen.getByRole("heading", { level: 3, name: "Files" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 3, name: "Case narrative" })).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 3, name: "Your answers (not sources)" }),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 2, name: "In this case 3" })).toBeInTheDocument();
  });

  it("lists each file once, by its latest reading, and keeps a turned-off source in its group", () => {
    const earlier = {
      ...documentSource(document, "First reading"),
      id: "reading-1",
      deactivated_at: "2026-10-17T01:00:00Z",
    };
    const latest = {
      ...documentSource(document, "Second reading"),
      id: "reading-2",
      created_at: "2026-10-17T01:00:00Z",
    };
    renderSources({
      sources: [earlier, latest, caseSource({ deactivated_at: "2026-10-17T02:00:00Z" })],
      onSetSourceActive: vi.fn().mockResolvedValue(undefined),
    });

    const files = screen.getByRole("heading", { level: 3, name: "Files" }).parentElement!;
    const narratives = screen.getByRole("heading", {
      level: 3,
      name: "Case narrative",
    }).parentElement!;
    expect(within(files).getAllByRole("button")).toHaveLength(1);
    expect(within(files).getByRole("checkbox")).toBeChecked();
    expect(within(narratives).getAllByRole("button")).toHaveLength(1);
    expect(within(narratives).getByRole("checkbox")).not.toBeChecked();
    expect(screen.queryByRole("heading", { level: 3, name: "Turned off" })).not.toBeInTheDocument();

    fireEvent.click(within(files).getByRole("button"));
    fireEvent.click(screen.getByRole("button", { name: "Text" }));
    expect(screen.getByText("Second reading")).toBeInTheDocument();
    expect(screen.queryByText("First reading")).not.toBeInTheDocument();
  });

  it("turns a source off with its checkbox in the rail", () => {
    const onSetSourceActive = vi.fn().mockResolvedValue(undefined);
    renderSources({ sources: [caseSource()], onSetSourceActive });

    expect(
      screen.queryByText("This source is turned off. The next analysis will not read it."),
    ).not.toBeInTheDocument();
    const checkbox = screen.getByRole("checkbox", {
      name: "Include in the analysis: Files on the shared drive were reported encrypted.",
    });
    expect(checkbox).toBeChecked();
    fireEvent.click(checkbox);

    expect(onSetSourceActive).toHaveBeenCalledWith("source-1", false);
  });

  it("switches a source that is not the one being read without changing the preview", () => {
    const onSetSourceActive = vi.fn().mockResolvedValue(undefined);
    renderSources({
      sources: [
        caseSource(),
        caseSource({ id: "source-2", exact_text: "The help desk logged a call." }),
      ],
      onSetSourceActive,
    });

    fireEvent.click(
      screen.getByRole("checkbox", {
        name: "Include in the analysis: The help desk logged a call.",
      }),
    );

    expect(onSetSourceActive).toHaveBeenCalledWith("source-2", false);
    expect(
      screen.getByRole("heading", { level: 2, name: /Files on the shared drive/ }),
    ).toBeInTheDocument();
  });

  it("has no checkbox for a follow-up answer, which is not a source", () => {
    renderSources({
      sources: [caseSource()],
      followups: [{ qaId: "QA-01", question: "Were backups kept?", answer: "Offline." }],
      onSetSourceActive: vi.fn().mockResolvedValue(undefined),
    });

    const answers = screen.getByRole("heading", {
      level: 3,
      name: "Your answers (not sources)",
    }).parentElement!;
    expect(within(answers).queryByRole("checkbox")).not.toBeInTheDocument();
    expect(screen.getAllByRole("checkbox")).toHaveLength(1);
  });

  it("keeps showing the source it turned off once the sources reload", () => {
    const first = caseSource();
    const second = caseSource({ id: "source-2", exact_text: "The help desk logged a call." });
    const props: React.ComponentProps<typeof CaseSourcesView> = {
      caseId: "case-1",
      sources: [first, second],
      followups: [],
      isUploading: false,
      isAddingNarrative: false,
      onUploadDocument: vi.fn(),
      onAddNarrative: vi.fn().mockResolvedValue(true),
      onSetSourceActive: vi.fn().mockResolvedValue(undefined),
    };
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const { rerender } = render(
      <QueryClientProvider client={queryClient}>
        <CaseSourcesView {...props} />
      </QueryClientProvider>,
    );

    fireEvent.click(
      screen.getByRole("checkbox", { name: /Include in the analysis: Files on the shared drive/ }),
    );
    rerender(
      <QueryClientProvider client={queryClient}>
        <CaseSourcesView
          {...props}
          sources={[{ ...first, deactivated_at: "2026-10-17T02:00:00Z" }, second]}
        />
      </QueryClientProvider>,
    );

    expect(
      screen.getByRole("heading", { level: 2, name: /Files on the shared drive/ }),
    ).toBeVisible();
    expect(
      screen.getByText("This source is turned off. The next analysis will not read it."),
    ).toBeInTheDocument();
    expect(screen.getAllByRole("checkbox")[0]).not.toBeChecked();
  });

  it("says a turned-off source is left out of the next analysis and turns it on when ticked", () => {
    const onSetSourceActive = vi.fn().mockResolvedValue(undefined);
    renderSources({
      sources: [caseSource({ deactivated_at: "2026-10-17T02:00:00Z" })],
      onSetSourceActive,
    });

    expect(
      screen.getByText("This source is turned off. The next analysis will not read it."),
    ).toBeInTheDocument();
    const checkbox = screen.getByRole("checkbox", { name: /Include in the analysis/ });
    expect(checkbox).not.toBeChecked();
    fireEvent.click(checkbox);

    expect(onSetSourceActive).toHaveBeenCalledWith("source-1", true);
  });

  it("does not offer to read a turned-off file again", () => {
    renderSources({
      sources: [
        {
          ...documentSource(document, "Received statement"),
          deactivated_at: "2026-10-17T02:00:00Z",
        },
      ],
      onRetryDocument: vi.fn().mockResolvedValue(undefined),
    });

    fireEvent.click(screen.getByRole("button", { name: "Text" }));

    expect(screen.queryByRole("button", { name: "Read the file again" })).not.toBeInTheDocument();
  });

  it("keeps a source switched as it is while an analysis runs", () => {
    renderSources({
      sources: [caseSource()],
      onSetSourceActive: vi.fn().mockResolvedValue(undefined),
      analysis: {
        freshness: "current",
        isRunning: true,
        isWaitingForFollowup: false,
        canAnalyze: false,
        onAnalyze: vi.fn(),
      },
    });

    expect(screen.getByRole("checkbox", { name: /Include in the analysis/ })).toBeDisabled();
  });

  it("reads a follow-up answer beside the question it answers", () => {
    renderSources({
      followups: [{ qaId: "QA-01", question: "มีหมายจับหรือไม่", answer: "ไม่มี" }],
    });

    expect(screen.getByText("Follow-up answer")).toBeInTheDocument();

    expect(screen.getByRole("heading", { level: 2, name: "มีหมายจับหรือไม่" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /มีหมายจับหรือไม่\s*ไม่มี/ })).toBeInTheDocument();
    const terms = screen.getAllByRole("term").map((term) => term.textContent);
    const definitions = screen.getAllByRole("definition").map((item) => item.textContent);
    expect(terms).toEqual(["Question", "Answer"]);
    expect(definitions).toEqual(["มีหมายจับหรือไม่", "ไม่มี"]);
  });

  it("shows Add narrative and Upload file as two visible buttons, with no menu", () => {
    renderSources({ sources: [caseSource()] });

    const narrative = screen.getByRole("button", { name: "Add narrative" });
    const upload = screen.getByRole("button", { name: "Upload file" });

    expect(narrative).toHaveTextContent("Add narrative");
    expect(narrative).toHaveClass("btn-primary");
    expect(narrative).not.toHaveAttribute("title");
    expect(upload).toHaveTextContent("Upload file");
    expect(upload).not.toHaveAttribute("title");
    expect(screen.queryByRole("button", { name: "Add source" })).not.toBeInTheDocument();
    expect(screen.queryByRole("menuitem")).not.toBeInTheDocument();
  });

  it("says why adding a source is unavailable while an analysis runs", () => {
    renderSources({
      sources: [caseSource()],
      analysis: {
        freshness: "current",
        isRunning: true,
        isWaitingForFollowup: false,
        canAnalyze: false,
        onAnalyze: vi.fn(),
      },
    });

    for (const name of ["Add narrative", "Upload file"]) {
      const button = screen.getByRole("button", { name });
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute("title", "Wait for the analysis to finish");
    }
  });

  it("adds a case narrative from the Add narrative button", async () => {
    const onAddNarrative = vi.fn().mockResolvedValue(true);
    renderSources({ sources: [caseSource()], onAddNarrative });

    fireEvent.click(screen.getByRole("button", { name: "Add narrative" }));

    fireEvent.change(screen.getByLabelText("Narrative"), {
      target: { value: "Files were encrypted overnight." },
    });
    fireEvent.click(screen.getAllByRole("button", { name: "Add narrative" }).at(-1)!);

    await waitFor(() =>
      expect(onAddNarrative).toHaveBeenCalledWith({ text: "Files were encrypted overnight." }),
    );
  });

  it("opens the file picker from the Upload file button", () => {
    renderSources({ sources: [caseSource()] });
    const input = screen.getByLabelText("Add file") as HTMLInputElement;
    const picker = vi.spyOn(input, "click").mockImplementation(() => {});

    fireEvent.click(screen.getByRole("button", { name: "Upload file" }));

    expect(picker).toHaveBeenCalledOnce();
  });

  it.each(["missing", "stale", "current"] as const)(
    "has no Analyze button in the rail with %s analysis",
    (freshness) => {
      renderSources({
        sources: [caseSource()],
        analysis: {
          freshness,
          isRunning: false,
          isWaitingForFollowup: false,
          canAnalyze: true,
          onAnalyze: vi.fn(),
        },
      });

      expect(screen.queryByRole("button", { name: /Analy[sz]/ })).not.toBeInTheDocument();
    },
  );

  it("tells the reader to use Analyze at the top until the sources have been read", () => {
    renderSources({
      sources: [caseSource()],
      analysis: {
        freshness: "missing",
        isRunning: false,
        isWaitingForFollowup: false,
        canAnalyze: true,
        onAnalyze: vi.fn(),
      },
    });

    expect(screen.getByRole("status")).toHaveTextContent(
      "Not analyzed yet. Use Analyze at the top when the sources are ready.",
    );
  });

  it("says when the sources changed since the last analysis", () => {
    renderSources({
      sources: [caseSource()],
      analysis: {
        freshness: "stale",
        isRunning: false,
        isWaitingForFollowup: false,
        canAnalyze: true,
        onAnalyze: vi.fn(),
      },
    });

    expect(screen.getByRole("status")).toHaveTextContent(
      "The analysis is out of date. Sources changed since it was made. Use Analyze at the top.",
    );
  });

  it.each(["missing", "current", "stale"] as const)(
    "says it is waiting for an answer, with %s analysis, and still lets a source be added",
    (freshness) => {
      renderSources({
        sources: [caseSource()],
        analysis: {
          freshness,
          isRunning: false,
          isWaitingForFollowup: true,
          canAnalyze: false,
          onAnalyze: vi.fn(),
        },
      });

      expect(screen.getByRole("status")).toHaveTextContent(
        "Waiting for your answer in Ask. The analysis continues when you answer.",
      );
      expect(screen.queryByRole("button", { name: /Analy[sz]/ })).not.toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Add narrative" })).toBeEnabled();
      expect(screen.getByRole("button", { name: "Upload file" })).toBeEnabled();
    },
  );

  it("keeps the rail clear once the analysis is up to date", () => {
    renderSources({
      sources: [caseSource()],
      analysis: {
        freshness: "current",
        isRunning: false,
        isWaitingForFollowup: false,
        canAnalyze: true,
        onAnalyze: vi.fn(),
      },
    });

    expect(screen.queryByRole("status")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Analy[sz]/ })).not.toBeInTheDocument();
  });

  it("shows a run in progress as a note, not a button", () => {
    renderSources({
      sources: [caseSource()],
      analysis: {
        freshness: "current",
        isRunning: true,
        isWaitingForFollowup: false,
        canAnalyze: false,
        onAnalyze: vi.fn(),
      },
    });

    expect(screen.getByRole("status")).toHaveTextContent("Analyzing the sources…");
    expect(screen.queryByRole("button", { name: /Analy[sz]/ })).not.toBeInTheDocument();
  });

  it("does not let a source be added while an analysis runs", () => {
    renderSources({
      sources: [caseSource()],
      analysis: {
        freshness: "current",
        isRunning: true,
        isWaitingForFollowup: false,
        canAnalyze: false,
        onAnalyze: vi.fn(),
      },
    });

    expect(screen.getByRole("button", { name: "Add narrative" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Upload file" })).toBeDisabled();
  });

  it("disables both add buttons when an analysis begins", () => {
    const props: React.ComponentProps<typeof CaseSourcesView> = {
      caseId: "case-1",
      sources: [caseSource()],
      followups: [],
      isUploading: false,
      isAddingNarrative: false,
      onUploadDocument: vi.fn(),
      onAddNarrative: vi.fn().mockResolvedValue(true),
      analysis: {
        freshness: "current",
        isRunning: false,
        isWaitingForFollowup: false,
        canAnalyze: true,
        onAnalyze: vi.fn(),
      },
    };
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const view = (running: boolean) => (
      <QueryClientProvider client={queryClient}>
        <CaseSourcesView
          {...props}
          analysis={{ ...props.analysis!, isRunning: running, canAnalyze: !running }}
        />
      </QueryClientProvider>
    );
    const { rerender } = render(view(false));
    expect(screen.getByRole("button", { name: "Add narrative" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Upload file" })).toBeEnabled();

    rerender(view(true));

    expect(screen.getByRole("button", { name: "Add narrative" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Upload file" })).toBeDisabled();
  });

  it("lets a source be added when no analysis runs", () => {
    renderSources({
      sources: [caseSource()],
      analysis: {
        freshness: "current",
        isRunning: false,
        isWaitingForFollowup: false,
        canAnalyze: true,
        onAnalyze: vi.fn(),
      },
    });

    expect(screen.getByRole("button", { name: "Add narrative" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Upload file" })).toBeEnabled();
    expect(screen.getByLabelText("Add file")).toBeEnabled();
  });

  it("waits for an upload to finish before more is added, and says the file is being read", () => {
    renderSources({
      sources: [caseSource()],
      isUploading: true,
      uploadingFilename: "statement.pdf",
      analysis: {
        freshness: "missing",
        isRunning: false,
        isWaitingForFollowup: false,
        canAnalyze: true,
        onAnalyze: vi.fn(),
      },
    });

    expect(screen.getByRole("button", { name: "Add narrative" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Upload file" })).toBeDisabled();
    expect(screen.getByRole("status")).toHaveTextContent("Reading the new file…");
  });

  it("marks a turned-off source as not used beside its checkbox", () => {
    renderSources({
      sources: [
        caseSource(),
        caseSource({
          id: "source-2",
          exact_text: "The help desk logged a call.",
          deactivated_at: "2026-10-17T02:00:00Z",
        }),
      ],
      onSetSourceActive: vi.fn().mockResolvedValue(undefined),
    });

    const used = screen.getByRole("checkbox", { name: /Include in the analysis: Files on/ });
    const unused = screen.getByRole("checkbox", { name: /Include in the analysis: The help desk/ });
    expect(used).toBeVisible();
    expect(used).toBeChecked();
    expect(unused).not.toBeChecked();
    expect(screen.getByRole("button", { name: /Files on the shared drive/ })).not.toHaveTextContent(
      "Not used",
    );
    expect(screen.getByRole("button", { name: /The help desk logged a call/ })).toHaveTextContent(
      "Not used ·",
    );
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
      expect(onAddNarrative).toHaveBeenCalledWith({ text: "A phishing email reached payroll." }),
    );
  });

  it("renders one card per extracted page", () => {
    renderSources(pagedDocument(2));
    fireEvent.click(screen.getByRole("button", { name: "Text" }));

    expect(screen.getByText("Page 1")).toBeInTheDocument();
    expect(screen.getByText("Page 1 content")).toBeInTheDocument();
    expect(screen.getByText("Page 2")).toBeInTheDocument();
    expect(screen.getByText("Page 2 content")).toBeInTheDocument();
    expect(screen.queryByRole("navigation", { name: "Page navigation" })).not.toBeInTheDocument();
  });

  it("offers page links once a document is long enough to need them", () => {
    renderSources(pagedDocument(5));
    fireEvent.click(screen.getByRole("button", { name: "Text" }));

    expect(screen.getByRole("navigation", { name: "Page navigation" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Go to page 1" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Go to page 5" })).toBeInTheDocument();
  });

  it("renders side-by-side comparison view with original file and extracted text", async () => {
    renderSources(pagedDocument(2));
    fireEvent.click(screen.getByRole("button", { name: "Side by side" }));

    expect(await screen.findByTitle("Original file: multi-page.pdf")).toBeInTheDocument();
    expect(screen.getByText("Page 1")).toBeInTheDocument();
    expect(screen.getByText("Page 1 content")).toBeInTheDocument();
  });

  it("calls the text of an OCR-read file machine-read and says to check it against the original", () => {
    renderSources({
      sources: [
        documentSource(document, "Received statement", {
          extraction_method: "document_recognition",
          verification_status: "machine_read",
          pages: [
            {
              page_number: 1,
              text: "Received statement",
              text_method: "ocr",
              verification_status: "machine_read",
            },
          ],
        }),
      ],
    });

    expect(screen.queryByRole("button", { name: "Text" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Text read from the file" }));

    expect(
      screen.getByText("Read by OCR. Check names, dates and numbers against the original."),
    ).toBeInTheDocument();
    expect(screen.getByText("Received statement")).toBeInTheDocument();
    expect(screen.queryByText("This page needs review against the original.")).toBeNull();
  });

  it("keeps Text and adds no line for a file whose text comes from the file itself", () => {
    renderSources({
      sources: [
        documentSource(document, "Received statement", {
          extraction_method: "native_docx",
          verification_status: "native",
          pages: [
            {
              page_number: 1,
              text: "Received statement",
              text_method: "native",
              verification_status: "native",
            },
          ],
        }),
      ],
    });

    fireEvent.click(screen.getByRole("button", { name: "Text" }));

    expect(
      screen.queryByRole("button", { name: "Text read from the file" }),
    ).not.toBeInTheDocument();
    expect(screen.queryByText(/Read by OCR/)).not.toBeInTheDocument();
  });

  it("says in words which page needs review against the original", () => {
    renderSources({
      sources: [
        documentSource(document, "first page", {
          extraction_method: "document_recognition",
          verification_status: "needs_review",
          pages: [
            {
              page_number: 1,
              text: "first page",
              text_method: "ocr",
              verification_status: "machine_read",
            },
            { page_number: 2, text: "", text_method: "ocr", verification_status: "needs_review" },
          ],
        }),
      ],
    });
    fireEvent.click(screen.getByRole("button", { name: "Text read from the file" }));

    const page = (number: number) =>
      screen.getByText(`Page ${number}`).closest("section") as HTMLElement;
    expect(within(page(2)).getByText("This page needs review against the original.")).toBeVisible();
    expect(within(page(1)).queryByText(/needs review/)).not.toBeInTheDocument();
    expect(screen.getAllByText("This page needs review against the original.")).toHaveLength(1);
  });

  it("shows the line in the side-by-side view too", async () => {
    renderSources({
      sources: [
        documentSource(document, "Received statement", {
          verification_status: "machine_read",
        }),
      ],
    });
    fireEvent.click(screen.getByRole("button", { name: "Side by side" }));

    expect(await screen.findByTitle("Original file: statement.pdf")).toBeInTheDocument();
    expect(screen.getByText(/Read by OCR/)).toBeInTheDocument();
  });

  it("renders the in-flight pending document item when uploading", () => {
    renderSources({ isUploading: true, uploadingFilename: "forensic_report.pdf" });

    expect(screen.getByText("forensic_report.pdf")).toBeInTheDocument();
    expect(screen.getByText("Reading the file…")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 2, name: "In this case 1" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "No sources yet" })).not.toBeInTheDocument();
  });
});
