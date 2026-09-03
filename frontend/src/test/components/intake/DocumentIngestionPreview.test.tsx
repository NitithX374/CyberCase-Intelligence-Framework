import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DocumentIngestionPreview } from "@/components/intake/DocumentIngestionPreview";
import * as ingestionApi from "@/lib/document-ingestion";
import { resetDocumentIngestionState, setDocumentIngestionMode } from "@/lib/document-ingestion-store";

const routedResult: ingestionApi.IngestedDocumentPreview = {
  document_id: "DOC-TEST",
  filename: "case.pdf",
  media_type: "application/pdf",
  extraction_method: "document_recognition",
  mode: "routed",
  pages: [
    {
      page_number: 1,
      merged_text: "ข้อความพิมพ์",
      routing_summary: {
        native: 0,
        unified: 0,
        ocr: 1,
        htr: 0,
        mixed: 0,
        unknown: 0,
      },
      regions: [
        {
          region_id: "DOC-TEST-P001-R001",
          page_number: 1,
          bbox: { x0: 10, y0: 20, x1: 300, y1: 60 },
          region_type: "printed_text",
          recognition_method: "ocr",
          recognizer: "typhoon-ocr",
          text: "ข้อความพิมพ์",
          confidence: null,
          verification_status: "machine_read",
          content_role: "transcribed_text",
          contains_handwriting: false,
          candidates: [],
          selected_candidate_index: null,
          generated_contents: [],
          warning: null,
        },
        {
          region_id: "DOC-TEST-P001-R002",
          page_number: 1,
          bbox: { x0: 10, y0: 80, x1: 300, y1: 120 },
          region_type: "handwriting",
          recognition_method: "none",
          recognizer: "none",
          text: "",
          confidence: null,
          verification_status: "needs_review",
          content_role: "transcribed_text",
          contains_handwriting: true,
          candidates: [],
          selected_candidate_index: null,
          generated_contents: [],
          warning: "HTR is disabled; manual transcription is required.",
        },
      ],
    },
  ],
  full_text: "ข้อความพิมพ์",
  warnings: ["HTR is disabled; manual transcription is required."],
};

describe("DocumentIngestionPreview", () => {
  beforeEach(() => {
    resetDocumentIngestionState();
    vi.restoreAllMocks();
  });

  it("uploads a document in unified mode by default with idempotency key", async () => {
    const preview = vi
      .spyOn(ingestionApi, "previewDocumentIngestion")
      .mockResolvedValue(routedResult);
    render(<DocumentIngestionPreview caseKey="case-001" />);
    const file = new File(["pdf"], "case.pdf", { type: "application/pdf" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Extract text/i }));

    await waitFor(() =>
      expect(preview).toHaveBeenCalledWith(
        file,
        "unified",
        expect.objectContaining({
          caseKey: "case-001",
          idempotencyKey: expect.stringContaining("case-001:case.pdf"),
        }),
      ),
    );
    expect(await screen.findByRole("heading", { name: "Review extracted content" })).toBeInTheDocument();
    expect(screen.getByText("Raw extraction details")).toBeInTheDocument();
    expect(screen.getByText("case.pdf · 1 pages")).toBeInTheDocument();
    expect(screen.getByText("1 extraction warning · Review required")).toBeInTheDocument();
  });

  it("preserves upload state and preview results across component unmount and remount", async () => {
    vi.spyOn(ingestionApi, "previewDocumentIngestion").mockResolvedValue(routedResult);
    const { unmount } = render(<DocumentIngestionPreview caseKey="case-persist" />);
    const file = new File(["pdf"], "case.pdf", { type: "application/pdf" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Extract text/i }));

    expect(await screen.findByRole("heading", { name: "Review extracted content" })).toBeInTheDocument();

    // Simulate navigating away to another tab
    unmount();

    // Simulate returning to the intake tab
    render(<DocumentIngestionPreview caseKey="case-persist" />);

    // Result and clear button are still rendered immediately without needing to re-upload
    expect(screen.getByRole("heading", { name: "Review extracted content" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Clear preview/i })).toBeInTheDocument();

    // Clear preview works as expected
    fireEvent.click(screen.getByRole("button", { name: /Clear preview/i }));
    expect(screen.queryByRole("heading", { name: "Review extracted content" })).not.toBeInTheDocument();
  });

  it("isolates OCR state and results across multiple cases using case keys", async () => {
    vi.spyOn(ingestionApi, "previewDocumentIngestion").mockResolvedValue(routedResult);

    // Case A
    const { unmount: unmountCaseA } = render(
      <DocumentIngestionPreview caseKey="case-A" />,
    );
    const fileA = new File(["pdf-A"], "caseA.pdf", { type: "application/pdf" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [fileA] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Extract text/i }));
    expect(await screen.findByRole("heading", { name: "Review extracted content" })).toBeInTheDocument();
    unmountCaseA();

    // Switch to Case B (which has no OCR preview yet)
    const { unmount: unmountCaseB } = render(
      <DocumentIngestionPreview caseKey="case-B" />,
    );
    expect(screen.queryByRole("heading", { name: "Review extracted content" })).not.toBeInTheDocument();
    expect(screen.queryByText(/Restored: caseA.pdf/i)).not.toBeInTheDocument();
    unmountCaseB();

    // Switch back to Case A (restores Case A's OCR result)
    render(<DocumentIngestionPreview caseKey="case-A" />);
    expect(screen.getByRole("heading", { name: "Review extracted content" })).toBeInTheDocument();
  });

  it("preserves the existing extraction mode without displaying settings", async () => {
    const preview = vi
      .spyOn(ingestionApi, "previewDocumentIngestion")
      .mockResolvedValue(routedResult);
    setDocumentIngestionMode("routed", "case-routed");
    render(<DocumentIngestionPreview caseKey="case-routed" />);
    expect(screen.queryByText("OCR settings")).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Recognition mode/i)).not.toBeInTheDocument();
    const file = new File(["image"], "page.png", { type: "image/png" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Extract text/i }));

    await waitFor(() =>
      expect(preview).toHaveBeenCalledWith(
        file,
        "routed",
        expect.objectContaining({
          caseKey: "case-routed",
          idempotencyKey: expect.stringContaining("case-routed:page.png"),
        }),
      ),
    );
  });

  it("hands reviewed merged text to the case narrative draft callback", async () => {
    vi.spyOn(ingestionApi, "previewDocumentIngestion").mockResolvedValue(routedResult);
    const onUseAsNarrative = vi.fn();
    render(
      <DocumentIngestionPreview
        caseKey="case-draft"
        onUseAsNarrative={onUseAsNarrative}
      />,
    );
    const file = new File(["pdf"], "case.pdf", { type: "application/pdf" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Extract text/i }));
    fireEvent.click(
      await screen.findByRole("button", {
        name: /Use reviewed text/i,
      }),
    );

    expect(onUseAsNarrative).toHaveBeenCalledWith({
      text: "ข้อความพิมพ์",
      pages: [],
      source: expect.objectContaining({
        document_id: "DOC-TEST",
        confidence_status: "not_reported",
        verification_status: "needs_review",
      }),
    });
  });

  it("shows a controlled provider error", async () => {
    const preview = vi.spyOn(ingestionApi, "previewDocumentIngestion")
      .mockRejectedValueOnce(new Error("OCR provider is unavailable."))
      .mockResolvedValueOnce(routedResult);
    render(<DocumentIngestionPreview caseKey="case-err" />);
    const file = new File(["image"], "page.jpg", { type: "image/jpeg" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Extract text/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "OCR provider is unavailable.",
    );
    fireEvent.click(screen.getByRole("button", { name: "Retry extraction" }));
    expect(await screen.findByRole("heading", { name: "Review extracted content" })).toBeInTheDocument();
    expect(preview).toHaveBeenCalledTimes(2);
    expect(preview.mock.calls[1]).toEqual(preview.mock.calls[0]);
  });
});
