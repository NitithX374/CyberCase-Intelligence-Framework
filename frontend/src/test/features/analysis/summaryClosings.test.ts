import { describe, expect, it } from "vitest";
import { noteLetter, summaryClosings } from "@/features/analysis/summaryClosings";

const CLOSINGS: [string, string[]][] = [
  ["A share was encrypted [A-01].", ["."]],
  ["First [A-01]. Second [A-02].", [".", "."]],
  ["It was found on October 1 [A-03], but the time is unknown [A-04].", [",", "."]],
  ["ไฟล์ถูกเข้ารหัส [A-01] ทีมพบกุญแจ [A-02]", ["", ""]],
  ["A [A-01] [A-02].", ["."]],
  ["A [A-01]. It then spread.", [".", ""]],
  ["No brackets at all.", [""]],
  ["One [A-01]。Two [A-02]", ["。", ""]],
  ["One [A-01]; two [A-02]!", [";", "!"]],
  ["One [A-01] ... two [A-02]", ["...", ""]],
  ["[A-01] Text [A-02].", ["."]],
  ["One [A-01]\n\nTwo [A-02]", ["", ""]],
  ["One [A-01] , two [A-02] .", [",", "."]],
];

describe("summaryClosings", () => {
  it.each(CLOSINGS)(
    "takes the punctuation after a bracket as its unit's closing: %s",
    (summary, closings) => {
      expect(summaryClosings(summary)).toEqual(closings);
    },
  );

  it("has nothing for an empty summary", () => {
    expect(summaryClosings("")).toEqual([]);
    expect(summaryClosings("  \n ")).toEqual([]);
  });
});

describe("noteLetter", () => {
  it.each([
    [0, "a"],
    [1, "b"],
    [25, "z"],
    [26, "aa"],
    [27, "ab"],
    [51, "az"],
    [52, "ba"],
    [701, "zz"],
    [702, "aaa"],
  ])("runs a to z and then aa, ab and so on: %i is %s", (index, letters) => {
    expect(noteLetter(index)).toBe(letters);
  });
});
