import { describe, expect, it } from "vitest";
import type { PersistedChatMessage } from "@/lib/api";
import {
  formatEvidenceCitationText,
  mapSourceMessageIds,
  parseEvidenceCitations,
} from "@/lib/evidence-citation";
import { sha256Hex } from "@/lib/sha256";

function message(
  content: string,
  documentSources: Record<string, unknown>[] = [],
): PersistedChatMessage {
  return {
    id: "source-1",
    thread_id: "thread-1",
    ordinal: 1,
    role: "user",
    content,
    retrieval_context_id: null,
    metadata_json: {
      evidence_kind: "initial_case_narrative",
      document_sources: documentSources,
    },
    created_at: "2026-09-02T00:00:00Z",
  };
}

function documentForPages(pages: Array<[number, string]>): Record<string, unknown> {
  let offset = 0;
  const pageSpans = pages.map(([pageNumber, text]) => {
    const span = {
      page_number: pageNumber,
      start_offset: offset,
      end_offset: offset + text.length,
      text_sha256: sha256Hex(text),
    };
    offset += text.length + 2;
    return span;
  });
  return {
    document_id: "DOC-1",
    filename: "statement.pdf",
    page_count: Math.max(...pages.map(([pageNumber]) => pageNumber)),
    page_spans: pageSpans,
  };
}

function citation(exactQuote: string, pageNumbers: number[]) {
  return {
    source_message_id: "source-1",
    exact_quote: exactQuote,
    document_id: pageNumbers.length > 0 ? "DOC-1" : null,
    filename: pageNumbers.length > 0 ? "statement.pdf" : null,
    page_numbers: pageNumbers,
  };
}

describe("evidence citation projection", () => {
  it("matches the standard SHA-256 digest", () => {
    expect(sha256Hex("Native narrative")).toBe(
      "e03d63dc82d71733cb48672c9606ff40af6519f20e5e14291572ebb78fddef7d",
    );
    expect(sha256Hex("บัญชีได้รับเงินจำนวน 52,000 บาท")).toBe(
      "679c5f9ef5581800349ba6b465363f6e28682bbc902c720cef6c42927179439c",
    );
  });

  it("admits an exact quote on one validated document page", () => {
    const content = "Page four: received 52,000 baht.";
    const source = message(content, [documentForPages([[4, content]])]);
    const [ref] = mapSourceMessageIds(
      [source.id],
      [source],
      parseEvidenceCitations([citation("received 52,000 baht", [4])]),
    );

    expect(ref.pageNumbers).toEqual([4]);
    expect(ref.filename).toBe("statement.pdf");
    expect(ref.evidencePages).toEqual([{
      pageNumber: 4,
      text: content,
      exactQuote: "received 52,000 baht",
    }]);
    expect(formatEvidenceCitationText(ref)).toBe("p. 4");
  });

  it("keeps consecutive and non-consecutive page references precise", () => {
    const consecutiveContent = "Page four text\n\nPage five text";
    const consecutiveSource = message(consecutiveContent, [
      documentForPages([[4, "Page four text"], [5, "Page five text"]]),
    ]);
    const [consecutive] = mapSourceMessageIds(
      [consecutiveSource.id],
      [consecutiveSource],
      parseEvidenceCitations([citation(consecutiveContent, [4, 5])]),
    );
    expect(formatEvidenceCitationText(consecutive)).toBe("pp. 4–5");
    expect(consecutive.evidencePages.map((page) => page.pageNumber)).toEqual([4, 5]);

    const nonConsecutiveContent = "Page four text\n\nPage seven text";
    const nonConsecutiveSource = message(nonConsecutiveContent, [
      documentForPages([[4, "Page four text"], [7, "Page seven text"]]),
    ]);
    const [nonConsecutive] = mapSourceMessageIds(
      [nonConsecutiveSource.id],
      [nonConsecutiveSource],
      parseEvidenceCitations([citation(nonConsecutiveContent, [4, 7])]),
    );
    expect(formatEvidenceCitationText(nonConsecutive)).toBe("pp. 4, 7");
  });

  it("falls back to a narrative source when a page hash is stale", () => {
    const content = "Page four: received 52,000 baht.";
    const document = documentForPages([[4, content]]);
    const pageSpans = document.page_spans as Record<string, unknown>[];
    pageSpans[0].text_sha256 = "0".repeat(64);
    const source = message(content, [document]);
    const [ref] = mapSourceMessageIds(
      [source.id],
      [source],
      parseEvidenceCitations([citation("received 52,000 baht", [4])]),
    );

    expect(ref.pageNumbers).toEqual([]);
    expect(ref.filename).toBeNull();
    expect(ref.label).toBe("Reviewed case narrative");
    expect(ref.displayContent).toContain("received 52,000 baht");
  });

  it("falls back when the document locator is incomplete", () => {
    const content = "Page four: received 52,000 baht.";
    const source = message(content, [documentForPages([[4, content]])]);
    const incompleteCitation = {
      ...citation("received 52,000 baht", [4]),
      document_id: null,
    };
    const [ref] = mapSourceMessageIds(
      [source.id],
      [source],
      parseEvidenceCitations([incompleteCitation]),
    );

    expect(ref.pageNumbers).toEqual([]);
    expect(ref.filename).toBeNull();
    expect(ref.label).toBe("Reviewed case narrative");
    expect(formatEvidenceCitationText(ref)).toBe("Case narrative");
  });

  it("keeps a narrative-only quote without fabricating a page", () => {
    const source = message("The witness saw a blue vehicle near the entrance.");
    const [ref] = mapSourceMessageIds(
      [source.id],
      [source],
      parseEvidenceCitations([citation("saw a blue vehicle", [])]),
    );

    expect(ref.pageNumbers).toEqual([]);
    expect(ref.filename).toBeNull();
    expect(formatEvidenceCitationText(ref)).toBe("Case narrative");
    expect(ref.exactQuote).toBe("saw a blue vehicle");
  });

  it("projects multiple validated citations from one source independently", () => {
    const content = "Page four has alpha. Page five has beta.";
    const source = message(content, [documentForPages([[4, content]])]);
    const refs = mapSourceMessageIds(
      [source.id],
      [source],
      parseEvidenceCitations([
        citation("alpha", [4]),
        citation("beta", [4]),
      ]),
    );

    expect(refs).toHaveLength(2);
    expect(refs.map((ref) => ref.exactQuote)).toEqual(["alpha", "beta"]);
  });
});
