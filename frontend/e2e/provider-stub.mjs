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
  const input = [...messages].reverse().find((message) => message?.role === "user" || message?.role === "human");
  return input?.content ?? messages[0]?.content ?? "";
}

function systemContent(body) {
  if (typeof body?.system === "string") return body.system;
  const messages = Array.isArray(body?.messages) ? body.messages : [];
  return messages.find((message) => message?.role === "system")?.content ?? "";
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
  const system = systemContent(body);
  const content = firstMessageContent(body);
  const request = asObject(content);
  const caseSources = Array.isArray(request?.case_sources)
    ? request.case_sources.filter(
        (source) => source && typeof source === "object" && typeof source.source_id === "string" && source.source_id,
      )
    : [];
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
  if (system.includes("analysis_mode is question_answer")) {
    const source = caseSources[0];
    return {
      answer: "The deterministic test provider answered from the current Case source.",
      cited_source_ids: source ? [source.source_id] : [],
      clarification_question: null,
    };
  }
  if (system.includes("You select the next single question")) {
    const asked = Array.isArray(request?.questions_asked) ? request.questions_asked : [];
    if (asked.length > 0) {
      return { action: "resolved", question: null, target_information: null };
    }
    return {
      action: "ask",
      question: "Which identification is correct: the primary operator or the secondary contractor?",
      target_information: "workstation owner",
      rationale_summary: "The current gap affects attribution of the workstation activity.",
    };
  }
  if (system.includes("You interpret one user's answer")) {
    const answer = request?.answer && typeof request.answer === "object" ? request.answer : {};
    const answerText = typeof answer.content === "string" ? answer.content : "";
    return {
      response_type: "case_fact",
      normalized_fact: answerText,
      resolved_information: answerText,
      gap_resolution: "resolved",
    };
  }
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

  const hasClarificationAnswer = caseSources.some((source) => source.source_kind === "followup_answer") || sections.length > 1;

  const gaps = (sourceText.includes("needs-clarification") && !hasClarificationAnswer)
    ? [
        {
          gap_id: "G-01",
          gap_key: "workstation_owner",
          topic: "Workstation Owner",
          status: "AMBIGUOUS",
          description: "Which identification is correct: the primary operator or the secondary contractor?",
          reason: "Clarifying workstation ownership is required to substantiate findings.",
          priority: "high",
          askable: true,
          clarification_question: "Which identification is correct: the primary operator or the secondary contractor?",
          affected_claim_ids: ["A-01"],
        },
      ]
    : [];

  return {
    version: "case_analysis_trace_v1",
    answer: `Deterministic E2E analysis: ${sourceText}`,
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
  const isAnthropic = request.url === "/v1/messages";
  const isOpenAi = request.url === "/v1/chat/completions";
  if (request.method !== "POST" || (!isAnthropic && !isOpenAi)) {
    sendJson(response, 404, { error: "not_found" });
    return;
  }
  requestCount += 1;
  try {
    const body = await readBody(request);
    const payload = responseFor(body);
    if (isOpenAi) {
      sendJson(response, 200, {
        id: `e2e-provider-${requestCount}`,
        object: "chat.completion",
        model: body?.model ?? "e2e-provider",
        choices: [{ index: 0, message: { role: "assistant", content: JSON.stringify(payload) }, finish_reason: "stop" }],
        usage: { prompt_tokens: 1, completion_tokens: 1, total_tokens: 2 },
      });
      return;
    }
    sendJson(response, 200, {
      id: `e2e-provider-${requestCount}`,
      model: body?.model ?? "e2e-provider",
      stop_reason: "end_turn",
      content: [{ type: "text", text: JSON.stringify(payload) }],
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
