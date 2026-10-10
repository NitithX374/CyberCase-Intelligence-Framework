import { describe, expect, it } from "vitest";
import type {
  CaseAnalysisResultRead,
  CaseMeaningPassage,
  CaseSourceCitation,
} from "@/lib/api/types";
import {
  analysisResult,
  claim,
  followupHistory,
  narrativeSource,
  pagedDocumentSource,
  sourceId,
  trace,
} from "@/test/fixtures";
import { buildCaseOverview, gapTopic } from "@/features/analysis/overview";

const quote = "The witness saw a blue vehicle.";

function result(
  text: string,
  citation: CaseSourceCitation,
  citedSourceId = sourceId,
): CaseAnalysisResultRead {
  return analysisResult({
    summary: text,
    trace_json: trace({
      summary: "The submitted material identifies a blue vehicle.",
      claims: [claim(text, citedSourceId, { supporting_citations: [citation] })],
    }),
  });
}

function pagedCitation(exactQuote: string, pageNumbers: number[]): CaseSourceCitation {
  return {
    source_id: sourceId,
    exact_quote: exactQuote,
    document_id: "DOC-1",
    filename: "statement.pdf",
    page_numbers: pageNumbers,
  };
}

describe("Case overview projection", () => {
  it("marks all LLM views as Claim-derived without offsets and preserves unknown time", () => {
    const overview = buildCaseOverview(
      analysisResult({
        trace_json: trace({
          claims: [claim("Company A suspended the account.")],
          view_extraction: {
            method: "llm",
            model: "test/model",
            input_claim_ids: ["A-01"],
            excluded_claim_ids: [],
            duration_ms: 120,
            status: "completed",
            items_dropped: 0,
          },
          involved_parties: [{ name: "Company A", role: null, claim_ids: ["A-01"] }],
          timeline: [{ time: null, event: "The account was suspended.", claim_ids: ["A-01"] }],
          impacts: [{ description: "An explicitly reported suspension.", claim_ids: ["A-01"] }],
        }),
      }),
      [narrativeSource("Company A suspended the account.")],
    );
    expect(overview.timeline[0].time).toBeNull();
    expect(overview.parties[0].linkedClaims).toEqual([
      { id: "A-01", text: "Company A suspended the account." },
    ]);
  });
  it("preserves the semantic verdict and linked claim text independently of binding", () => {
    const grounding = { verdict: "not_supported", reason: "neutral" } as const;
    const overview = buildCaseOverview(
      analysisResult({
        trace_json: trace({
          claims: [claim("John sent an email.")],
          involved_parties: [
            {
              name: "John",
              role: "Attacker",
              claim_ids: ["A-01"],
              support: "bound",
              projection_grounding: grounding,
            },
          ],
        }),
      }),
      [narrativeSource("John sent an email.")],
    );
    expect(overview.parties[0].linkedClaims).toEqual([{ id: "A-01", text: "John sent an email." }]);
    expect(overview.parties[0].supportNote).toBe(
      "The linked findings do not support this description.",
    );
  });
  const supported = (summary: string) =>
    analysisResult({
      summary,
      trace_json: trace({
        summary,
        claims: [claim("A", sourceId, { supporting_citations: [] })],
        involved_parties: [
          { name: "Finance", role: "Victim", claim_ids: ["A-01"], support: "mixed" },
          { name: "Intruder", role: "Attacker", claim_ids: ["A-01"], support: "bound" },
        ],
        timeline: [
          { time: "Monday", event: "Encrypted", claim_ids: ["A-01"], support: "unbound" },
          { time: "Tuesday", event: "Ransom", claim_ids: [], support: "no_claim" },
        ],
        impacts: [{ description: "Payroll lost", claim_ids: ["A-01"] }],
      }),
    });

  it("gives each party, event and impact the line its status calls for", () => {
    const overview = buildCaseOverview(supported("A share was encrypted."), [
      narrativeSource(quote),
    ]);

    expect(overview.parties.map((row) => row.supportNote)).toEqual([
      "Only some linked claims have resolved source citations.",
      null,
    ]);
    expect(overview.timeline.map((row) => row.supportNote)).toEqual([
      "None of the linked claims has a resolved source citation.",
      "Not linked to any claim.",
    ]);
    expect(overview.impacts.map((row) => row.supportNote)).toEqual([null]);
  });

  it("writes the lines in Thai when the analysis is in Thai", () => {
    const overview = buildCaseOverview(supported("ไฟล์ถูกเข้ารหัสในช่วงกลางคืน"), [
      narrativeSource(quote),
    ]);

    expect(overview.timeline.map((row) => row.supportNote)).toEqual([
      "ยังระบุตำแหน่งข้อความอ้างอิงใน Source ของข้อค้นพบที่เชื่อมไว้ไม่ได้",
      "ไม่ได้เชื่อมกับข้อสังเกตใด",
    ]);
  });

  const unitsOf = (summary: string) =>
    analysisResult({
      summary,
      trace_json: trace({
        summary,
        claims: [
          claim("A", sourceId),
          claim("B", sourceId, { claim_id: "A-02", supporting_citations: [] }),
          claim("C", sourceId, { claim_id: "A-03", supporting_citations: [] }),
        ],
        summary_units: [
          { text: "A share was encrypted", claim_ids: ["A-01"], support: "bound" },
          { text: "Both demands", claim_ids: ["A-01", "A-02"], support: "mixed" },
          { text: "Ten bitcoin", claim_ids: ["A-03"], support: "unbound" },
          { text: "Someone is to blame", claim_ids: [], support: "no_claim" },
        ],
      }),
    });

  it("gives each summary unit its finding marks and the line its status calls for", () => {
    const overview = buildCaseOverview(unitsOf("A share was encrypted [A-01]."), [
      narrativeSource(quote),
    ]);

    expect(
      overview.summaryUnits.map(({ text, marks, supportNote, noteMark }) => ({
        text,
        marks,
        supportNote,
        noteMark,
      })),
    ).toEqual([
      {
        text: "A share was encrypted",
        marks: [{ number: 1, claimId: "A-01" }],
        supportNote: null,
        noteMark: null,
      },
      {
        text: "Both demands",
        marks: [
          { number: 1, claimId: "A-01" },
          { number: 2, claimId: "A-02" },
        ],
        supportNote: "Only some linked claims have resolved source citations.",
        noteMark: "a",
      },
      {
        text: "Ten bitcoin",
        marks: [{ number: 3, claimId: "A-03" }],
        supportNote: "None of the linked claims has a resolved source citation.",
        noteMark: "b",
      },
      {
        text: "Someone is to blame",
        marks: [],
        supportNote: "Not linked to any claim.",
        noteMark: "c",
      },
    ]);
  });

  it("writes the summary lines in Thai when the summary is in Thai", () => {
    const overview = buildCaseOverview(unitsOf("ไฟล์ถูกเข้ารหัส [A-01]"), [narrativeSource(quote)]);

    expect(overview.summaryUnits.map((unit) => unit.supportNote)).toEqual([
      null,
      "ระบุตำแหน่งข้อความอ้างอิงใน Source ได้สำหรับข้อค้นพบที่เชื่อมไว้บางข้อ",
      "ยังระบุตำแหน่งข้อความอ้างอิงใน Source ของข้อค้นพบที่เชื่อมไว้ไม่ได้",
      "ไม่ได้เชื่อมกับข้อสังเกตใด",
    ]);
  });

  it("has no summary units for an analysis stored before they existed", () => {
    const overview = buildCaseOverview(supported("A share was encrypted."), [
      narrativeSource(quote),
    ]);

    expect(overview.summaryUnits).toEqual([]);
    expect(overview.incidentSummary).toBe("A share was encrypted.");
  });

  it("renders claims from current case sources", () => {
    const overview = buildCaseOverview(result(quote, { source_id: sourceId, exact_quote: quote }), [
      narrativeSource(quote),
    ]);
    const source = overview.findings[0].supportingSources[0];
    expect(overview.incidentSummary).toContain("blue vehicle");
    expect(source).toMatchObject({ id: sourceId, label: "Case narrative #1", exactQuote: quote });
  });

  it("carries what the locator tolerated onto the quotation, in the language of the analysis", () => {
    const citation: CaseSourceCitation = {
      source_id: sourceId,
      exact_quote: quote,
      tolerated_differences: [{ written: "apple", source: "Apple" }],
    };
    const english = buildCaseOverview(result(quote, citation), [narrativeSource(quote)]);
    const thai = buildCaseOverview(
      analysisResult({
        summary: "ไฟล์ถูกเข้ารหัสในช่วงกลางคืน",
        trace_json: trace({
          summary: "ไฟล์ถูกเข้ารหัสในช่วงกลางคืน",
          claims: [claim(quote, sourceId, { supporting_citations: [citation] })],
        }),
      }),
      [narrativeSource(quote)],
    );

    expect(english.findings[0].supportingSources[0].toleratedNotes).toEqual([
      "Found in the source when formatting is ignored. The analysis wrote «apple»; the source says «Apple».",
    ]);
    expect(thai.findings[0].supportingSources[0].toleratedNotes).toEqual([
      "พบในเอกสารเมื่อไม่นับรูปแบบ — ข้อความวิเคราะห์เขียน «apple» เอกสารเขียน «Apple»",
    ]);
  });

  it("carries the marks to check onto the quotation, in the language of the analysis", () => {
    const citation: CaseSourceCitation = {
      source_id: sourceId,
      exact_quote: quote,
      review_flags: [{ kind: "meaning_mark", verdict: "rule_warning", detail: "? edge" }],
    };
    const english = buildCaseOverview(result(quote, citation), [narrativeSource(quote)]);
    const thai = buildCaseOverview(
      analysisResult({
        summary: "ไฟล์ถูกเข้ารหัสในช่วงกลางคืน",
        trace_json: trace({
          summary: "ไฟล์ถูกเข้ารหัสในช่วงกลางคืน",
          claims: [claim(quote, sourceId, { supporting_citations: [citation] })],
        }),
      }),
      [narrativeSource(quote)],
    );

    expect(english.findings[0].supportingSources[0].reviewNotes).toEqual([
      "Check: the source has the mark ? next to the quote, which the quote leaves out.",
    ]);
    expect(thai.findings[0].supportingSources[0].reviewNotes).toEqual([
      "ตรวจ: ต้นฉบับมีเครื่องหมาย ? ที่ quote ไม่ได้รวมไว้",
    ]);
  });

  it("gives a quotation with no flag no mark line, and a flag changes no status", () => {
    const overview = buildCaseOverview(result(quote, { source_id: sourceId, exact_quote: quote }), [
      narrativeSource(quote),
    ]);
    const flagged = buildCaseOverview(
      result(quote, {
        source_id: sourceId,
        exact_quote: quote,
        review_flags: [{ kind: "meaning_mark", verdict: "rule_warning", detail: "? edge" }],
      }),
      [narrativeSource(quote)],
    );

    expect(overview.findings[0].supportingSources[0].reviewNotes).toBeUndefined();
    expect(flagged.findings[0].epistemicStatus).toBe(overview.findings[0].epistemicStatus);
    expect(flagged.findings[0].supportingSources).toHaveLength(
      overview.findings[0].supportingSources.length,
    );
  });

  const unlocated = (summary: string, meaning: CaseMeaningPassage | null) =>
    analysisResult({
      summary,
      trace_json: trace({
        summary,
        claims: [
          claim("A file share was encrypted overnight.", sourceId, {
            epistemic_status: "not_confirmed",
            supporting_citations: [],
            unverified_citations: [
              {
                source_id: sourceId,
                role: "supporting",
                written_quote: "Something else entirely.",
                near_passage: null,
                ...(meaning ? { meaning_passage: meaning } : {}),
              },
            ],
          }),
        ],
      }),
    });
  const found = {
    source_text: quote,
    start: 0,
    end: quote.length,
    entailment: 0.97,
    model: "mdeberta",
  };

  it("carries the passage found by meaning onto the unverified quote, in the language of the analysis", () => {
    const english = buildCaseOverview(unlocated("A share was encrypted.", found), [
      narrativeSource(quote),
    ]);
    const thai = buildCaseOverview(unlocated("ไฟล์ถูกเข้ารหัสในช่วงกลางคืน", found), [
      narrativeSource(quote),
    ]);

    const [fromEnglish] = english.findings[0].unverifiedQuotes;
    const [fromThai] = thai.findings[0].unverifiedQuotes;
    expect(fromEnglish.meaningPassage).toMatchObject({
      exactQuote: quote,
      quoteLabel: "A passage in the source that may be related (found by meaning, not confirmed)",
    });
    expect(fromThai.meaningPassage?.quoteLabel).toBe(
      "ข้อความในต้นฉบับที่อาจเกี่ยวข้อง (หาจากความหมาย ยังไม่ยืนยัน)",
    );
    expect(english.findings[0].epistemicStatus).toBe("not_confirmed");
    expect(
      english.findings[0].supportingSources.every((source) => source.exactQuote === null),
    ).toBe(true);
  });

  it("has no meaning passage when the analysis found none, or was stored before", () => {
    const none = buildCaseOverview(unlocated("A share was encrypted.", null), [
      narrativeSource(quote),
    ]);

    expect(none.findings[0].unverifiedQuotes[0].meaningPassage).toBeNull();
  });

  it("never shows the score of a meaning passage", () => {
    const overview = buildCaseOverview(unlocated("A share was encrypted.", found), [
      narrativeSource(quote),
    ]);

    expect(JSON.stringify(overview)).not.toContain("0.97");
    expect(JSON.stringify(overview)).not.toContain("entailment");
  });

  it("gives a quotation found as written no tolerated line", () => {
    const overview = buildCaseOverview(result(quote, { source_id: sourceId, exact_quote: quote }), [
      narrativeSource(quote),
    ]);

    expect(overview.findings[0].supportingSources[0].toleratedNotes).toBeUndefined();
  });

  it("shows the pages the stored citation names", () => {
    const documentQuote = "Defendant was seen at the scene.";
    const overview = buildCaseOverview(result(documentQuote, pagedCitation(documentQuote, [1])), [
      pagedDocumentSource(documentQuote, 1),
    ]);
    expect(overview.hasAnalysis).toBe(true);
    expect(overview.findings[0].supportingSources[0]).toMatchObject({
      label: "statement.pdf · p. 1",
      pageNumbers: [1],
    });
  });

  it("keeps the stored page of a quote that appears more than once", () => {
    const repeatedQuote = "Suspicious vehicle reported.";
    const fullText = `${repeatedQuote}\nSome intermediate text.\n${repeatedQuote}`;
    const overview = buildCaseOverview(result(repeatedQuote, pagedCitation(repeatedQuote, [1])), [
      pagedDocumentSource(fullText, 1),
    ]);
    expect(overview.findings[0].supportingSources[0].pageNumbers).toEqual([1]);
  });

  it("cuts a page where the backend counted it, in characters", () => {
    const first = "หน้า 1 😀 received";
    const second = "Page two records the transfer.";
    const text = `${first}\n${second}`;
    const firstLength = Array.from(first).length + 1;
    const source = pagedDocumentSource(text, 1, {
      provenance_json: {
        pages: [
          { page_number: 1, start_offset: 0, end_offset: firstLength },
          {
            page_number: 2,
            start_offset: firstLength,
            end_offset: firstLength + Array.from(second).length,
          },
        ],
      },
    });

    const overview = buildCaseOverview(result(second, pagedCitation(second, [2])), [source]);

    expect(overview.findings[0].supportingSources[0].sourcePages).toEqual([
      { pageNumber: 2, text: second },
    ]);
  });

  it("keeps a citation the stored sources do not hold out of the finding", () => {
    const overview = buildCaseOverview(
      result(quote, { source_id: "missing", exact_quote: quote }, "missing"),
      [narrativeSource(quote)],
    );
    expect(overview.hasAnalysis).toBe(true);
    expect(overview.findings[0].supportingSources).toEqual([]);
  });

  it("cites a follow-up answer from the exchange the analysis recorded", () => {
    const answer = "The incident occurred at 02:00.";
    const followupResult = {
      ...result(answer, { source_id: "QA-02", exact_quote: answer }, "QA-02"),
      external_context_json: {
        followup_history: followupHistory("When did the incident occur?", answer, "QA-02"),
      },
    };

    const overview = buildCaseOverview(followupResult, []);

    expect(overview.findings[0].supportingSources[0]).toMatchObject({
      id: "QA-02",
      label: "Follow-up answer QA-02",
      question: "When did the incident occur?",
      exactQuote: answer,
    });
  });

  it("does not cite a follow-up answer the analysis did not record", () => {
    const answer = "The incident occurred at 02:00.";
    const overview = buildCaseOverview(
      result(answer, { source_id: "QA-01", exact_quote: answer }, "QA-01"),
      [],
    );

    expect(overview.hasAnalysis).toBe(true);
    expect(overview.findings[0].supportingSources).toEqual([]);
  });

  it("lists parties, timeline and impacts with the sources of the claims they cite", () => {
    const base = result(quote, { source_id: sourceId, exact_quote: quote });
    const inference = {
      ...base.trace_json!.claims[0],
      claim_id: "A-02",
      claim_type: "analytical_inference" as const,
      epistemic_status: "suspected" as const,
    };
    const analysis: CaseAnalysisResultRead = {
      ...base,
      trace_json: {
        ...base.trace_json!,
        claims: [...base.trace_json!.claims, inference],
        involved_parties: [{ name: "Witness", role: "Saw the vehicle", claim_ids: ["A-01"] }],
        timeline: [
          { time: "09:00", event: "A blue vehicle arrived", claim_ids: ["A-01", "A-02"] },
          { time: "Unknown", event: "Nothing cited", claim_ids: [] },
        ],
        impacts: [{ description: "The owner may be exposed", claim_ids: ["A-02"] }],
      },
    };

    const overview = buildCaseOverview(analysis, [narrativeSource(quote)]);

    expect(overview.parties).toEqual([
      expect.objectContaining({ name: "Witness", role: "Saw the vehicle", inferred: false }),
    ]);
    expect(overview.parties[0].sources.map((source) => source.id)).toEqual([sourceId]);
    expect(overview.timeline[0].sources).toHaveLength(1);
    expect(overview.timeline[0].inferred).toBe(false);
    expect(overview.timeline[1]).toMatchObject({ sources: [], inferred: false });
    expect(overview.impacts[0].inferred).toBe(true);
  });

  it("carries each unverified quote with its places and a way to the nearest passage", () => {
    const text = "The transfer happened on 17 March 2026 at noon.";
    const base = result(text, { source_id: sourceId, exact_quote: text });
    const analysis: CaseAnalysisResultRead = {
      ...base,
      trace_json: {
        ...base.trace_json!,
        claims: [
          {
            ...base.trace_json!.claims[0],
            epistemic_status: "not_confirmed" as const,
            supporting_citations: [],
            unverified_citations: [
              {
                source_id: sourceId,
                role: "supporting" as const,
                written_quote: "The transfer happened on 11 March 2026",
                near_passage: {
                  source_text: "The transfer happened on 17 March 2026",
                  differences: [{ written: "11", source: "17" }],
                  occurrences: 1,
                },
              },
              {
                source_id: "missing",
                role: "supporting" as const,
                written_quote: "Something else",
                near_passage: null,
              },
            ],
          },
        ],
      },
    };

    const [first, second] = buildCaseOverview(analysis, [narrativeSource(text)]).findings[0]
      .unverifiedQuotes;

    expect(first.places).toEqual([{ written: "11", source: "17" }]);
    expect(first.passage).toMatchObject({
      id: sourceId,
      exactQuote: "The transfer happened on 17 March 2026",
      quoteLabel: "Nearest passage",
    });
    expect(second).toEqual({
      places: [],
      passage: null,
      meaningPassage: null,
    });
  });

  it("links each finding to the ATT&CK techniques associated with it", () => {
    const base = result(quote, { source_id: sourceId, exact_quote: quote });
    const analysis: CaseAnalysisResultRead = {
      ...base,
      trace_json: {
        ...base.trace_json!,
        mitre_associations: [
          {
            association_id: "MA-01",
            technique_id: "T1566",
            claim_ids: ["A-01"],
            reason: "A phishing email was reported.",
            plain_meaning: "",
            status: "candidate_only",
            support_role: "external_technical_context",
          },
        ],
      },
    };

    const overview = buildCaseOverview(analysis, [narrativeSource(quote)]);

    expect(overview.findings[0].techniqueIds).toEqual(["T1566"]);
  });

  it("names the findings each gap affects, in the gap's order, leaving out ids no finding has", () => {
    const base = result(quote, { source_id: sourceId, exact_quote: quote });
    const later = { ...base.trace_json!.claims[0], claim_id: "A-02", text: "It left at noon." };
    const gap = {
      gap_id: "G-01",
      gap_key: "when",
      topic: "when",
      status: "NOT_PROVIDED" as const,
      description: "The time the vehicle arrived is not given.",
      reason: "The time places the vehicle at the scene.",
      priority: "high" as const,
      askable: true,
    };
    const analysis: CaseAnalysisResultRead = {
      ...base,
      trace_json: {
        ...base.trace_json!,
        claims: [...base.trace_json!.claims, later],
        gaps: [
          { ...gap, affected_claim_ids: ["A-02", "A-09", "A-01"] },
          { ...gap, gap_id: "G-02" },
        ],
      },
    };

    const overview = buildCaseOverview(analysis, [narrativeSource(quote)]);

    expect(overview.gaps.map((item) => item.affectedFindings)).toEqual([
      [
        { id: "A-02", text: "It left at noon." },
        { id: "A-01", text: quote },
      ],
      [],
    ]);
  });
});

describe("Case overview rows backed by claims that are not settled", () => {
  const otherSourceId = "33333333-3333-4333-8333-333333333333";
  const first = "The witness saw a blue vehicle.";
  const second = "The driver was seen leaving at noon.";

  const analysis: CaseAnalysisResultRead = analysisResult({
    summary: first,
    trace_json: trace({
      summary: first,
      claims: [
        claim(first),
        claim(second, otherSourceId, {
          claim_id: "A-02",
          epistemic_status: "not_confirmed",
          supporting_citations: [],
        }),
        claim(first, sourceId, {
          claim_id: "A-03",
          claim_type: "analytical_inference",
          epistemic_status: "suspected",
        }),
        claim(second, otherSourceId, {
          claim_id: "A-04",
          claim_type: "analytical_inference",
          epistemic_status: "suspected",
          supporting_citations: [],
        }),
      ],
      timeline: [
        { time: "1", event: "Settled", claim_ids: ["A-01"] },
        { time: "2", event: "Not confirmed only", claim_ids: ["A-02"] },
        { time: "3", event: "Settled and not confirmed", claim_ids: ["A-01", "A-02"] },
        { time: "4", event: "Suspected with a checked quote", claim_ids: ["A-03"] },
        { time: "5", event: "Suspected on a named source", claim_ids: ["A-04"] },
        { time: "6", event: "Both kinds", claim_ids: ["A-04", "A-02"] },
        { time: "7", event: "Names no claim", claim_ids: [] },
      ],
    }),
  });
  const sources = [narrativeSource(first), narrativeSource(second, { id: otherSourceId })];
  const timeline = buildCaseOverview(analysis, sources).timeline;

  it("adds no note to a row whose claims are settled, or that names none", () => {
    expect(timeline[0].unconfirmed).toEqual([]);
    expect(timeline[0].sources.map((source) => source.id)).toEqual([sourceId]);
    expect(timeline[6]).toMatchObject({ sources: [], unconfirmed: [] });
  });

  it("shows no source chip for a claim that is not confirmed, and says so", () => {
    expect(timeline[1]).toMatchObject({ sources: [], unconfirmed: ["not_confirmed"] });
  });

  it("keeps the chips of the settled claims in a row and says the rest is not confirmed", () => {
    expect(timeline[2].sources.map((source) => source.id)).toEqual([sourceId]);
    expect(timeline[2].unconfirmed).toEqual(["not_confirmed"]);
  });

  it("keeps the chip of a suspected claim only where a checked quote stands behind it", () => {
    expect(timeline[3].sources).toHaveLength(1);
    expect(timeline[3].sources[0]).toMatchObject({ id: sourceId, exactQuote: first });
    expect(timeline[3].unconfirmed).toEqual(["suspected"]);
    expect(timeline[4]).toMatchObject({ sources: [], unconfirmed: ["suspected"] });
  });

  it("names each kind once, the missing check first", () => {
    expect(timeline[5].unconfirmed).toEqual(["not_confirmed", "suspected"]);
  });

  it("marks parties and impacts the same way", () => {
    const overview = buildCaseOverview(
      {
        ...analysis,
        trace_json: {
          ...analysis.trace_json!,
          involved_parties: [{ name: "Driver", role: "Left at noon", claim_ids: ["A-02"] }],
          impacts: [{ description: "The vehicle was gone", claim_ids: ["A-04"] }],
        },
      },
      sources,
    );

    expect(overview.parties[0]).toMatchObject({ sources: [], unconfirmed: ["not_confirmed"] });
    expect(overview.impacts[0]).toMatchObject({ sources: [], unconfirmed: ["suspected"] });
  });
});

describe("gap topics", () => {
  it("names a checklist key in words", () => {
    expect(gapTopic("how_much", "how_much")).toBe("How much");
    expect(gapTopic("who_responsible", "who_responsible")).toBe("Who carried it out");
  });

  it("spells out a key of the analysis's own when it stands in for the topic", () => {
    expect(gapTopic("log_file_exists", "log_file_exists")).toBe("Log file exists");
  });

  it("keeps a topic that is not its key", () => {
    expect(gapTopic("มูลค่าทรัพย์สิน", "how_much")).toBe("มูลค่าทรัพย์สิน");
  });
});
