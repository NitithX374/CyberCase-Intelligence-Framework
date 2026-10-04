import { describe, expect, it } from "vitest";
import { hasThai } from "@/lib/language";

describe("hasThai", () => {
  it("tells Thai text from the rest", () => {
    expect(hasThai("ไฟล์ถูกเข้ารหัส")).toBe(true);
    expect(hasThai("A file was encrypted, 51,001 baht")).toBe(false);
    expect(hasThai("")).toBe(false);
  });

  it("finds a Thai character anywhere in mixed text", () => {
    expect(hasThai("Invoice ๑๒๓ was paid")).toBe(true);
    expect(hasThai("The file was named ไฟล์.pdf")).toBe(true);
  });
});
