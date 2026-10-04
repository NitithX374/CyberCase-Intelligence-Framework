import { describe, expect, it } from "vitest";
import { reviewNotes } from "@/features/citations/reviewNotes";

const flag = (detail: string) => ({ kind: "meaning_mark", verdict: "rule_warning", detail });

describe("reviewNotes", () => {
  it("says in English that the source has a mark next to the quote", () => {
    expect(reviewNotes([flag("? edge")], "A share was encrypted.")).toEqual([
      "Check: the source has the mark ? next to the quote, which the quote leaves out.",
    ]);
  });

  it("says in English that the quote and the source differ at a mark", () => {
    expect(reviewNotes([flag("~ % ignored")], "A share was encrypted.")).toEqual([
      "Check: the quote and the source differ at the mark ~ %, which may change the meaning.",
    ]);
  });

  it("says both in Thai when the analysis is in Thai", () => {
    expect(reviewNotes([flag("? edge"), flag("~ ignored")], "ไฟล์ถูกเข้ารหัส")).toEqual([
      "ตรวจ: ต้นฉบับมีเครื่องหมาย ? ที่ quote ไม่ได้รวมไว้",
      "ตรวจ: ต้นฉบับกับ quote ต่างกันที่เครื่องหมาย ~ ซึ่งอาจเปลี่ยนความหมาย",
    ]);
  });

  it("gives one line per flag, in order", () => {
    expect(reviewNotes([flag("< edge"), flag("> edge")], "x")).toHaveLength(2);
  });

  it("says nothing for no flags, an unknown kind, or a detail it cannot read", () => {
    expect(reviewNotes([], "x")).toEqual([]);
    expect(reviewNotes(undefined, "x")).toEqual([]);
    expect(
      reviewNotes(
        [
          { kind: "entailment", verdict: "rule_warning", detail: "? edge" },
          flag("? nearby"),
          flag("edge"),
          flag(""),
        ],
        "x",
      ),
    ).toEqual([]);
  });
});
