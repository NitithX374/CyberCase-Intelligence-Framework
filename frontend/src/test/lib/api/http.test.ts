import { afterEach, describe, expect, it, vi } from "vitest";
import { uploadCaseDocument } from "@/features/sources/api";
import { http } from "@/lib/api/http";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("how long the browser waits for work the backend is still doing", () => {
  const uploadWorstCaseMs = Math.ceil(50 / 4) * 60_000;

  function timeoutOf(post: ReturnType<typeof vi.spyOn>): number {
    const [, , config] = post.mock.calls[0] as [string, unknown, { timeout?: number }];
    return config.timeout ?? 0;
  }

  it("waits for an upload longer than reading the longest scan it accepts", async () => {
    const post = vi.spyOn(http, "post").mockResolvedValue({ data: {} });

    await uploadCaseDocument("case-1", new File(["%PDF"], "scan.pdf"));

    expect(timeoutOf(post)).toBeGreaterThan(uploadWorstCaseMs);
  });
});
