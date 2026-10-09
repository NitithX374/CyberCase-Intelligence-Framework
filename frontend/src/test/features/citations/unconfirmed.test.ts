import { describe, expect, it } from "vitest";
import type { SourceMessageRef } from "@/features/citations/types";
import {
  checkedSources,
  isUnconfirmed,
  NO_CHECKED_QUOTE,
  UNCONFIRMED_NOTES,
  unconfirmedStatuses,
} from "@/features/citations/unconfirmed";

function source(id: string, exactQuote: string | null): SourceMessageRef {
  return {
    id,
    label: id,
    displayContent: "",
    exactQuote,
    quoteContext: null,
    filename: null,
    pageNumbers: [],
    sourcePages: [],
    question: null,
  };
}

describe("claims that are not confirmed or only suspected", () => {
  it("tells those two statuses from every other", () => {
    expect(isUnconfirmed("not_confirmed")).toBe(true);
    expect(isUnconfirmed("suspected")).toBe(true);
    for (const status of ["reported", "contradicted", "not_established", "unknown", undefined]) {
      expect(isUnconfirmed(status)).toBe(false);
    }
  });

  it("lists each kind once, the missing check first, and ignores the rest", () => {
    expect(
      unconfirmedStatuses(["suspected", "reported", undefined, "not_confirmed", "suspected"]),
    ).toEqual(["not_confirmed", "suspected"]);
    expect(unconfirmedStatuses(["reported", "unknown"])).toEqual([]);
    expect(unconfirmedStatuses([])).toEqual([]);
  });

  it("keeps every source of a settled claim", () => {
    const sources = [source("a", "a quote"), source("b", null)];
    expect(checkedSources(sources, false)).toEqual(sources);
  });

  it("keeps only the sources with a checked quote for a claim that is not settled", () => {
    const quoted = source("a", "a quote");
    expect(checkedSources([quoted, source("b", null)], true)).toEqual([quoted]);
  });

  it("pins the Thai wording of the notes", () => {
    expect(NO_CHECKED_QUOTE).toBe("ไม่มี quote ที่ตรวจแล้ว");
    expect(UNCONFIRMED_NOTES).toEqual({
      not_confirmed: "ยังไม่ยืนยัน ไม่มี quote ที่ตรวจแล้ว",
      suspected: "อยู่ระหว่างตรวจสอบ",
    });
  });
});
