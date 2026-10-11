import { afterEach, describe, expect, it, vi } from "vitest";
import { uploadCaseDocument } from "@/features/sources/api";
import { apiBaseUrl, http } from "@/lib/api/http";

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

describe("which host the browser reaches the API on", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it.each([
    ["http://localhost:8000/api/v1", "127.0.0.1", "http://127.0.0.1:8000/api/v1"],
    ["http://127.0.0.1:8000/api/v1", "localhost", "http://localhost:8000/api/v1"],
    ["http://localhost:8000", "127.0.0.1", "http://127.0.0.1:8000/api/v1"],
    ["http://localhost:8000/api/v1", "[::1]", "http://[::1]:8000/api/v1"],
    ["http://localhost:8000/api/v1", "localhost", "http://localhost:8000/api/v1"],
  ])(
    "sends %s to the loopback host the page was opened on (%s)",
    (configured, pageHost, expected) => {
      vi.stubEnv("NEXT_PUBLIC_API_URL", configured);

      expect(apiBaseUrl(pageHost)).toBe(expected);
    },
  );

  it.each([
    ["https://api.example.com/api/v1", "127.0.0.1"],
    ["http://localhost:8000/api/v1", "192.168.1.20"],
    ["http://localhost:8000/api/v1", "cybercase.example.com"],
  ])("keeps %s as configured when the page is on %s", (configured, pageHost) => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", configured);

    expect(apiBaseUrl(pageHost)).toBe(configured);
  });

  it("keeps the configured host when there is no page", () => {
    vi.stubEnv("NEXT_PUBLIC_API_URL", "http://localhost:8000/api/v1");

    expect(apiBaseUrl(null)).toBe("http://localhost:8000/api/v1");
  });
});
