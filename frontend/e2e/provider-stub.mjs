import http from "node:http";

const port = Number(process.env.PROVIDER_PORT ?? 8099);
let requestCount = 0;

function readBody(request) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    request.on("data", (chunk) => chunks.push(chunk));
    request.on("end", () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")));
      } catch (error) {
        reject(error);
      }
    });
    request.on("error", reject);
  });
}

function sendJson(response, status, payload) {
  const body = JSON.stringify(payload);
  response.writeHead(status, {
    "content-type": "application/json",
    "content-length": Buffer.byteLength(body),
  });
  response.end(body);
}

function firstMessageContent(body) {
  const messages = Array.isArray(body?.messages) ? body.messages : [];
  return messages[0]?.content ?? "";
}

function asObject(value) {
  if (value && typeof value === "object" && !Array.isArray(value)) return value;
  if (typeof value !== "string") return null;
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

function responseFor(body) {
  const system = typeof body?.system === "string" ? body.system : "";
  const content = firstMessageContent(body);
  if (system.includes("MITRE ATT&CK applicability gate")) {
    return {
      decision: "SKIP",
      source_message_ids: [],
      trigger_text: [],
    };
  }
  if (typeof content === "string" && content.includes("Return all relevant case-specific gaps")) {
    return { gaps: [] };
  }
  if (system.includes("Answer only the current question")) {
    return {
      insufficient_context: false,
      units: [
        {
          text: "The deterministic test provider answered from the persisted case analysis.",
          claim_ids: ["A-01"],
        },
      ],
    };
  }
  const request = asObject(content);
  const evidence = typeof request?.raw_case_evidence === "string" ? request.raw_case_evidence : "";
  const sourceIds = Array.isArray(request?.authoritative_case_source_ids)
    ? request.authoritative_case_source_ids.filter((value) => typeof value === "string" && value)
    : [];
  if (!evidence || sourceIds.length === 0) {
    throw new Error("Unsupported E2E provider request");
  }
  const sourceId = sourceIds[0];
  const quote = evidence.split(/\]\n/).at(-1)?.trim() || evidence.trim();
  return {
    version: "case_analysis_trace_v1",
    answer: `Deterministic E2E analysis: ${evidence}`,
    summary: `Deterministic E2E summary: ${evidence}`,
    claims: [
      {
        claim_id: "A-01",
        claim_type: "reported",
        text: quote,
        epistemic_status: "reported",
        supporting_source_ids: [sourceId],
        contradicting_source_ids: [],
        supporting_citations: [
          {
            source_id: sourceId,
            source_revision: 1,
            exact_quote: quote,
          },
        ],
        contradicting_citations: [],
      },
    ],
    mitre_associations: [],
  };
}

const server = http.createServer(async (request, response) => {
  if (request.method === "GET" && request.url === "/health") {
    sendJson(response, 200, { status: "ok", requests: requestCount });
    return;
  }
  if (request.method !== "POST" || request.url !== "/v1/messages") {
    sendJson(response, 404, { error: "not_found" });
    return;
  }
  requestCount += 1;
  try {
    const body = await readBody(request);
    sendJson(response, 200, {
      id: `e2e-provider-${requestCount}`,
      model: body?.model ?? "e2e-provider",
      stop_reason: "end_turn",
      content: [{ type: "text", text: JSON.stringify(responseFor(body)) }],
      usage: { input_tokens: 1, output_tokens: 1 },
    });
  } catch (error) {
    sendJson(response, 400, { error: error instanceof Error ? error.message : "invalid_request" });
  }
});

server.listen(port, "127.0.0.1");
const stop = () => server.close(() => process.exit(0));
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
