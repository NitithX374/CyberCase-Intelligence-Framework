import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DocumentIngestionPreview } from "@/components/intake/DocumentIngestionPreview";
import * as ingestionApi from "@/lib/document-ingestion";
import { resetDocumentIngestionState } from "@/lib/document-ingestion-store";

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

  it("uploads a document in unified mode by default", async () => {
    const preview = vi
      .spyOn(ingestionApi, "previewDocumentIngestion")
      .mockResolvedValue(routedResult);
    render(<DocumentIngestionPreview />);
    const file = new File(["pdf"], "case.pdf", { type: "application/pdf" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Run OCR preview/i }));

    await waitFor(() => expect(preview).toHaveBeenCalledWith(file, "unified"));
    expect(await screen.findByText("DOC-TEST-P001-R001")).toBeInTheDocument();
    expect(screen.getByText("DOC-TEST-P001-R002")).toBeInTheDocument();
    expect(screen.getByText(/typhoon-ocr/i)).toBeInTheDocument();
    expect(screen.getAllByText(/HTR is disabled; manual transcription is required/i)).toHaveLength(2);
  });

  it("preserves upload state and preview results across component unmount and remount", async () => {
    vi.spyOn(ingestionApi, "previewDocumentIngestion").mockResolvedValue(routedResult);
    const { unmount } = render(<DocumentIngestionPreview />);
    const file = new File(["pdf"], "case.pdf", { type: "application/pdf" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Run OCR preview/i }));

    expect(await screen.findByText("DOC-TEST-P001-R001")).toBeInTheDocument();

    // Simulate navigating away to another tab
    unmount();

    // Simulate returning to the intake tab
    render(<DocumentIngestionPreview />);

    // Result and clear button are still rendered immediately without needing to re-upload
    expect(screen.getByText("DOC-TEST-P001-R001")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Clear preview/i })).toBeInTheDocument();

    // Clear preview works as expected
    fireEvent.click(screen.getByRole("button", { name: /Clear preview/i }));
    expect(screen.queryByText("DOC-TEST-P001-R001")).not.toBeInTheDocument();
  });

  it("keeps the routed contract available for future comparison", async () => {
    const preview = vi
      .spyOn(ingestionApi, "previewDocumentIngestion")
      .mockResolvedValue(routedResult);
    render(<DocumentIngestionPreview />);
    const file = new File(["image"], "page.png", { type: "image/png" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [file] },
    });
    fireEvent.change(screen.getByLabelText(/Recognition mode/i), {
      target: { value: "routed" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Run OCR preview/i }));

    await waitFor(() => expect(preview).toHaveBeenCalledWith(file, "routed"));
  });

  it("shows a controlled provider error", async () => {
    vi.spyOn(ingestionApi, "previewDocumentIngestion").mockRejectedValue(
      new Error("OCR provider is unavailable."),
    );
    render(<DocumentIngestionPreview />);
    const file = new File(["image"], "page.jpg", { type: "image/jpeg" });

    fireEvent.change(screen.getByLabelText(/Document for OCR preview/i), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Run OCR preview/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "OCR provider is unavailable.",
    );
  });
});
