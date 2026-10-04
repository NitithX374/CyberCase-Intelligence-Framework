import { describe, expect, it } from "vitest";
import { httpError, networkError, refusal, timeoutError } from "@/test/httpErrors";
import { isCaseNotFound } from "@/lib/userFacingError";

describe("isCaseNotFound", () => {
  it("recognises the refusal the backend sends for a missing or foreign case", () => {
    expect(isCaseNotFound(refusal(404, "case_not_found", "Case not found"))).toBe(true);
  });

  it.each([
    ["another code on the same status", refusal(404, "document_not_found", "Document not found")],
    ["the same code on another status", refusal(409, "case_not_found", "Case not found")],
    ["a status with no code", httpError(404, "Not Found")],
    ["a server error", httpError(500, "Internal Server Error")],
    ["a lost connection", networkError()],
    ["a timeout", timeoutError()],
    ["a plain error", new Error("case_not_found")],
    ["nothing", null],
  ])("does not mistake %s for it", (_name, error) => {
    expect(isCaseNotFound(error)).toBe(false);
  });
});
