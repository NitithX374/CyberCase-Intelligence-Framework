import { describe, expect, it } from "vitest";
import {
  bindCaseNarrativeDocumentSource,
  buildCaseNarrativeDraft,
} from "@/lib/case-narrative-document";
import type { IngestedDocumentPreview } from "@/lib/document-ingestion";
import { sha256Hex } from "@/lib/sha256";

function nativeDocument(): IngestedDocumentPreview {
  return {
    document_id: "DOC-NATIVE-1",
    filename: "native.pdf",
    media_type: "application/pdf",
    extraction_method: "native_pdf",
    mode: "unified",
    pages: [
      {
        page_number: 1,
        merged_text: "Native narrative",
        text_sha256: sha256Hex("Native narrative"),
        routing_summary: {
          native: 1,
          unified: 0,
          ocr: 0,
          htr: 0,
          mixed: 0,
          unknown: 0,
        },
        regions: [
          {
            region_id: "DOC-NATIVE-1-P001-R001",
            page_number: 1,
            bbox: null,
            region_type: "printed_text",
            recognition_method: "native",
            recognizer: "native-pdf",
            text: "Native narrative",
            segmentation_confidence: null,
            recognition_confidence: null,
            words: [],
            verification_status: "native",
            content_role: "transcribed_text",
            contains_handwriting: false,
            candidates: [],
            selected_candidate_index: null,
            generated_contents: [],
            warning: null,
          },
        ],
      },
    ],
    full_text: "Native narrative",
    warnings: ["A non-text figure was omitted."],
  };
}

describe("buildCaseNarrativeDraft", () => {
  it("does not mislabel native text as missing OCR confidence", () => {
    const draft = buildCaseNarrativeDraft(nativeDocument());
    expect(draft.source.verification_status).toBe("needs_review");
    expect(draft.source.confidence_status).toBe("not_applicable");
    expect(draft.source.minimum_confidence).toBeNull();
  });

  it("binds a document page only while its extracted text remains exact", () => {
    const draft = buildCaseNarrativeDraft(nativeDocument());
    const unchanged = bindCaseNarrativeDocumentSource(draft, draft.text);
    const edited = bindCaseNarrativeDocumentSource(draft, "Reviewed narrative");

    expect(unchanged.page_spans).toEqual([{
      page_number: 1,
      start_offset: 0,
      end_offset: 16,
      text_sha256: sha256Hex("Native narrative"),
    }]);
    expect(edited.page_spans).toEqual([]);
  });

  it("preserves unchanged OCR page provenance", () => {
    const document = nativeDocument();
    document.extraction_method = "document_recognition";
    document.mode = "routed";
    document.pages[0].routing_summary = {
      native: 0,
      unified: 0,
      ocr: 1,
      htr: 0,
      mixed: 0,
      unknown: 0,
    };
    document.pages[0].regions[0].recognition_method = "ocr";
    document.pages[0].regions[0].recognizer = "typhoon-ocr";
    document.pages[0].regions[0].verification_status = "needs_review";
    document.pages[0].regions[0].segmentation_confidence = 0.94;

    const draft = buildCaseNarrativeDraft(document);
    const bound = bindCaseNarrativeDocumentSource(draft, draft.text);

    expect(bound.page_spans).toHaveLength(1);
    expect(bound.page_spans[0].text_sha256).toBe(sha256Hex("Native narrative"));
    expect(bound.confidence_status).toBe("not_reported");
    expect(bound.minimum_confidence).toBeNull();
  });

  it("uses recognition minima across OCR regions without sending words downstream", () => {
    const document = nativeDocument();
    document.warnings = [];
    const region = document.pages[0].regions[0];
    region.verification_status = "machine_read";
    region.recognizer = "google_vision";
    region.recognition_method = "ocr";
    region.segmentation_confidence = 0.99;
    region.recognition_confidence = 0.71;
    region.words = [{ text: "52,000", confidence: 0.71, bbox: null }];
    document.pages[0].regions.push({ ...region, recognition_confidence: 0.42 });
    const draft = buildCaseNarrativeDraft(document);
    expect(draft.source.confidence_status).toBe("reported");
    expect(draft.source.minimum_confidence).toBe(0.42);
    expect(draft.source.verification_status).toBe("machine_read");
    expect(draft.source).not.toHaveProperty("words");
  });

  it("retains zero recognition confidence without adding a review threshold", () => {
    const document = nativeDocument();
    document.warnings = [];
    document.pages[0].regions[0].verification_status = "machine_read";
    document.pages[0].regions[0].recognition_confidence = 0;
    const draft = buildCaseNarrativeDraft(document);
    expect(draft.source.confidence_status).toBe("reported");
    expect(draft.source.minimum_confidence).toBe(0);
    expect(draft.source.verification_status).toBe("machine_read");
  });

  it("does not claim complete confidence coverage when an OCR region has no measurements", () => {
    const document = nativeDocument();
    const region = document.pages[0].regions[0];
    region.verification_status = "machine_read";
    region.recognition_confidence = 0.71;
    document.pages[0].regions.push({ ...region, recognition_confidence: null });
    expect(buildCaseNarrativeDraft(document).source.confidence_status).toBe("not_reported");
  });
});
