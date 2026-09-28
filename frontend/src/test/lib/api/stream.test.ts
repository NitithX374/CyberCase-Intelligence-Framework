import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { startCaseAnalysis } from "@/features/analysis/api";
import { createCaseChatMessage } from "@/features/chat/api";
import { toUserFacingError } from "@/lib/userFacingError";
import { postWithProgress, type StreamedStep } from "@/lib/api/stream";

const encoder = new TextEncoder();

function streamOf(chunks: string[], gapMs = 0): ReadableStream<Uint8Array> {
  return new ReadableStream({
    async start(controller) {
      for (const chunk of chunks) {
        if (gapMs) await new Promise((resolve) => setTimeout(resolve, gapMs));
        controller.enqueue(encoder.encode(chunk));
      }
      controller.close();
    },
  });
}

function respondWith(body: BodyInit | null, init: ResponseInit = { status: 200 }) {
  const fetchMock = vi.fn<(url: string, init: RequestInit) => Promise<Response>>(
    async () => new Response(body, init),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function step(name: string, elapsed: number): string {
  return `event: step\ndata: ${JSON.stringify({ step: name, elapsed })}\n\n`;
}

function result(data: unknown): string {
  return `event: result\ndata: ${JSON.stringify(data)}\n\n`;
}

async function failureOf(promise: Promise<unknown>): Promise<unknown> {
  try {
    await promise;
  } catch (error) {
    return error;
  }
  throw new Error("expected the request to fail");
}

beforeEach(() => {
  vi.stubEnv("NEXT_PUBLIC_API_URL", "http://api.test");
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

describe("the requests that start work on a case", () => {
  it("starts an analysis without a language, because the backend decides it", async () => {
    const fetchMock = respondWith(streamOf([result({ status: "need_followup" })]));

    await startCaseAnalysis("case-1");

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://api.test/api/v1/cases/case-1/analysis");
    expect(init).toMatchObject({ method: "POST", body: "{}", credentials: "include" });
    expect(init.headers).toMatchObject({ Accept: "text/event-stream" });
  });

  it("sends a chat message without a language, whatever it is written in", async () => {
    const fetchMock = respondWith(streamOf([result({ messages: [] })]));

    await createCaseChatMessage("case-1", "02:00", "key-1");

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://api.test/api/v1/cases/case-1/chat/messages");
    expect(JSON.parse(init.body as string)).toEqual({
      content: "02:00",
      client_request_id: "key-1",
    });
  });
});

describe("reading the progress of work the backend is still doing", () => {
  it("hands each step to the caller, then resolves with the result", async () => {
    const whole = step("assess", 0.1) + ": heartbeat\n\n" + step("read", 12.4) + result({ ok: 1 });
    respondWith(streamOf([whole.slice(0, 30), whole.slice(30, 75), whole.slice(75)]));
    const steps: StreamedStep[] = [];

    const value = await postWithProgress("/x", {}, { onStep: (reached) => steps.push(reached) });

    expect(steps).toEqual([
      { step: "assess", elapsed: 0.1 },
      { step: "read", elapsed: 12.4 },
    ]);
    expect(value).toEqual({ ok: 1 });
  });

  it("gives a refusal in the stream the same message a refused response gets", async () => {
    const detail = { code: "case_sources_missing", message: "Add a source first" };
    respondWith(
      streamOf([
        step("assess", 0),
        `event: error\ndata: ${JSON.stringify({ status: 422, detail })}\n\n`,
      ]),
    );

    const error = await failureOf(postWithProgress("/x", {}, { onStep: () => undefined }));

    expect(toUserFacingError(error)).toMatchObject({
      category: "refused",
      message: "กรุณาเพิ่มแหล่งข้อมูลของคดีก่อนเริ่มการวิเคราะห์",
    });
  });

  it("reads a refusal that comes before the stream as the response it is", async () => {
    respondWith(JSON.stringify({ detail: { code: "case_not_found", message: "Case not found" } }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });

    const error = await failureOf(postWithProgress("/x", {}, { onStep: () => undefined }));

    expect(toUserFacingError(error)).toMatchObject({
      category: "refused",
      message: "ไม่พบคดีนี้ หรือคดีถูกลบไปแล้ว",
    });
  });

  it("gives up as a timeout when the server goes quiet", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async (_url: string, init: RequestInit) =>
          new Response(
            new ReadableStream({
              start(controller) {
                init.signal?.addEventListener("abort", () =>
                  controller.error(new DOMException("aborted", "AbortError")),
                );
              },
            }),
          ),
      ),
    );

    const error = await failureOf(
      postWithProgress("/x", {}, { onStep: () => undefined, idleTimeoutMs: 20 }),
    );

    expect(toUserFacingError(error).category).toBe("timeout");
  });

  it("keeps waiting for as long as the heartbeats keep coming", async () => {
    respondWith(streamOf([...Array(5).fill(": heartbeat\n\n"), result({ ok: 1 })], 10));

    await expect(
      postWithProgress("/x", {}, { onStep: () => undefined, idleTimeoutMs: 40 }),
    ).resolves.toEqual({ ok: 1 });
  });

  it("fails as a lost connection when the stream ends without a result", async () => {
    respondWith(streamOf([step("read", 3)]));

    const error = await failureOf(postWithProgress("/x", {}, { onStep: () => undefined }));

    expect(toUserFacingError(error).category).toBe("network");
  });
});
