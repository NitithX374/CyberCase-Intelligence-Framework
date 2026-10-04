import { describe, expect, it } from "vitest";
import { toleratedNotes } from "@/features/citations/toleratedNotes";

describe("toleratedNotes", () => {
  it("says in English what the analysis wrote and what the source says", () => {
    expect(
      toleratedNotes([{ written: "apple", source: "Apple" }], "A share was encrypted."),
    ).toEqual([
      "Found in the source when formatting is ignored. The analysis wrote «apple»; the source says «Apple».",
    ]);
  });

  it("says in Thai what the analysis wrote and what the source says", () => {
    expect(toleratedNotes([{ written: "apple", source: "Apple" }], "ไฟล์ถูกเข้ารหัส")).toEqual([
      "พบในเอกสารเมื่อไม่นับรูปแบบ — ข้อความวิเคราะห์เขียน «apple» เอกสารเขียน «Apple»",
    ]);
  });

  it("words a difference that has only one side", () => {
    const dash = [{ written: "", source: "-" }];
    const added = [{ written: "5,000", source: "" }];

    expect(toleratedNotes(dash, "x")).toEqual([
      "Found in the source when formatting is ignored. The source has «-», which the analysis leaves out.",
    ]);
    expect(toleratedNotes(added, "x")).toEqual([
      "Found in the source when formatting is ignored. The analysis adds «5,000».",
    ]);
    expect(toleratedNotes(dash, "ไฟล์")).toEqual([
      "พบในเอกสารเมื่อไม่นับรูปแบบ — เอกสารมี «-» ที่ข้อความวิเคราะห์ตัดออก",
    ]);
    expect(toleratedNotes(added, "ไฟล์")).toEqual([
      "พบในเอกสารเมื่อไม่นับรูปแบบ — ข้อความวิเคราะห์เติม «5,000»",
    ]);
  });

  it("gives one line per difference, and none when there are none", () => {
    expect(
      toleratedNotes(
        [
          { written: "resign", source: "re-sign" },
          { written: "the rapist", source: "therapist" },
        ],
        "x",
      ),
    ).toHaveLength(2);
    expect(toleratedNotes([], "x")).toEqual([]);
    expect(toleratedNotes(undefined, "x")).toEqual([]);
  });
});
