import { describe, expect, it } from "vitest";
import { supportNote } from "@/features/analysis/supportNote";

describe("supportNote", () => {
  it("says nothing for an item whose claims are all bound, or when no status was recorded", () => {
    expect(supportNote("bound", "A file share was encrypted.")).toBeNull();
    expect(supportNote(null, "A file share was encrypted.")).toBeNull();
    expect(supportNote(undefined, "A file share was encrypted.")).toBeNull();
  });

  it("describes the citation in the language the analysis was written in", () => {
    expect(supportNote("unbound", "A file share was encrypted.")).toBe(
      "No cited quotation was found in the sources.",
    );
    expect(supportNote("mixed", "A file share was encrypted.")).toBe(
      "Some cited quotations were not found in the sources.",
    );
    expect(supportNote("no_claim", "A file share was encrypted.")).toBe("Not linked to any claim.");
    expect(supportNote("unbound", "ไฟล์ถูกเข้ารหัสในช่วงกลางคืน")).toBe(
      "ไม่พบข้อความที่อ้างในเอกสาร",
    );
    expect(supportNote("mixed", "ไฟล์ถูกเข้ารหัสในช่วงกลางคืน")).toBe(
      "ข้อความที่อ้างบางส่วนไม่พบในเอกสาร",
    );
    expect(supportNote("no_claim", "ไฟล์ถูกเข้ารหัสในช่วงกลางคืน")).toBe(
      "ไม่ได้เชื่อมกับข้อสังเกตใด",
    );
  });

  it("does not say that the fact itself was not confirmed", () => {
    for (const status of ["unbound", "mixed", "no_claim"] as const) {
      expect(supportNote(status, "x")).not.toMatch(/fact|true|false/i);
    }
  });
});
