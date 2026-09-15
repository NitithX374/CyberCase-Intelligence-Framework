import { describe, expect, it } from "vitest";
import { detectResponseLanguage } from "@/lib/api";

describe("detectResponseLanguage", () => {
  it("detects Thai input", () => {
    expect(detectResponseLanguage("ตรวจสอบเหตุการณ์นี้ให้หน่อย")).toBe("thai");
  });

  it("detects English input", () => {
    expect(detectResponseLanguage("Summarize this case.")).toBe("english");
  });

  it("uses Thai when input contains both Thai and English", () => {
    expect(detectResponseLanguage("Case นี้ต้องตรวจสอบอะไรต่อ")).toBe("thai");
  });

  it("keeps the contract for input without alphabetic characters", () => {
    expect(detectResponseLanguage("123 !?")).toBe("english");
  });
});
