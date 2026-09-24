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

function assessedGaps(request) {
  const sources = Array.isArray(request?.case_sources) ? request.case_sources : [];
  const history = Array.isArray(request?.followup_history) ? request.followup_history : [];
  const text = sources
    .map((source) => (typeof source?.text === "string" ? source.text : ""))
    .join("\n");
  const answered = history.some((item) => typeof item?.answer === "string" && item.answer.trim());
  if (!text.includes("needs-clarification") || answered) return [];
  return [
    {
      gap_id: "G-01",
      gap_key: "workstation_owner",
      topic: "Workstation Owner",
      status: "AMBIGUOUS",
      description:
        "Which identification is correct: the primary operator or the secondary contractor?",
      reason: "Clarifying workstation ownership is required to substantiate findings.",
      priority: "high",
      askable: true,
      clarification_question:
        "Which identification is correct: the primary operator or the secondary contractor?",
      affected_claim_ids: [],
    },
  ];
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
  if (system.includes("case_assessment_v1")) {
    return { version: "case_assessment_v1", gaps: assessedGaps(asObject(content)) };
  }
  if (system.includes("Answer only the current question")) {
    return {
      outcome: "answered",
      units: [
        {
          text: "The deterministic test provider answered from the persisted case analysis.",
          claim_ids: ["A-01"],
        },
      ],
    };
  }
  const request = asObject(content);
  const caseSources = Array.isArray(request?.case_sources)
    ? request.case_sources.filter(
        (source) =>
          source &&
          typeof source === "object" &&
          typeof source.source_id === "string" &&
          source.source_id,
      )
    : [];
  if (caseSources.length === 0) {
    throw new Error("Unsupported E2E provider request");
  }

  const sections = caseSources.map((source) => ({
    sourceId: source.source_id,
    quote: typeof source.text === "string" ? source.text.trim() : "",
  }));
  const sourceText = sections.map((section) => section.quote).join("\n\n");

  const claims = sections.map((sec, idx) => ({
    claim_id: `A-0${idx + 1}`,
    claim_type: "reported",
    text: sec.quote,
    epistemic_status: "reported",
    supporting_source_ids: [sec.sourceId],
    contradicting_source_ids: [],
    supporting_citations: [
      {
        source_id: sec.sourceId,
        exact_quote: sec.quote,
      },
    ],
    contradicting_citations: [],
  }));

  const followupHistory = Array.isArray(request?.followup_history) ? request.followup_history : [];
  const hasClarificationAnswer =
    followupHistory.some((item) => item && typeof item.answer === "string" && item.answer.trim()) ||
    caseSources.some((source) => source.source_kind === "followup_answer") ||
    sections.length > 1;

  const gaps =
    sourceText.includes("needs-clarification") && !hasClarificationAnswer
      ? [
          {
            gap_id: "G-01",
            gap_key: "workstation_owner",
            topic: "Workstation Owner",
            status: "AMBIGUOUS",
            description:
              "Which identification is correct: the primary operator or the secondary contractor?",
            reason: "Clarifying workstation ownership is required to substantiate findings.",
            priority: "high",
            askable: true,
            clarification_question:
              "Which identification is correct: the primary operator or the secondary contractor?",
            affected_claim_ids: ["A-01"],
          },
        ]
      : [];

  return {
    version: "case_analysis_trace_v1",
    summary: `Deterministic E2E summary: ${sourceText}`,
    involved_parties: [],
    timeline: [],
    impacts: [],
    claims,
    gaps,
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
