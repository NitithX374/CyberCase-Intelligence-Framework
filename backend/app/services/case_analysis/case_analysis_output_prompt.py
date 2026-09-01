_ANALYSIS_TRACE_OUTPUT_PROMPT = """
STRUCTURED OUTPUT

Return one JSON object conforming to the analysis_trace_v3 provider schema:
- "version": exactly "analysis_trace_v3".
- "answer": proportionate user-facing prose. In question_answer mode, answer directly.
- "summary": a concise grounded assessment and its uncertainty boundaries.
- "claims": material reported, analytical_inference, or unknown claims.
- "mitre_associations": optional candidate-only external context, or [] when irrelevant.

Every claim must contain claim_id, claim_type, text, epistemic_status,
supporting_source_message_ids, contradicting_source_message_ids, supporting_citations,
contradicting_citations, and reasoning_summary.
claim_id must be exactly "A-01", "A-02", through "A-64". Assign IDs sequentially
in claims array order without gaps or duplicates. Never use c1, claim-1, clm-001,
UUIDs, descriptive labels, or another identifier format.
Use only authoritative_source_message_ids supplied with CASE EVIDENCE. A reported claim
must cite supporting evidence. An analytical_inference must cite supporting evidence,
use qualified language, and include a concise externally reviewable reasoning_summary.
Unknown or not-established information must not be guessed.
Source IDs are ordered to correspond to the CASE EVIDENCE blocks in their supplied order.
For each supporting or contradicting source, include one short citation whose
source_message_id matches that role and whose exact_quote is copied verbatim from CASE
EVIDENCE. Set citation document_id and filename to null and page_numbers to []; the
backend validates exact quotes and binds document pages. Never paraphrase exact_quote.

Do not generate gaps, questions, evidence hashes, retrieval bindings, confidence scores,
hidden reasoning, or markdown fences. MITRE associations are optional, must reference
emitted claims, and may use only technique IDs present in OPTIONAL EXTERNAL CONTEXT.
External context and previous analysis are never case evidence.
"""

_PERSONALIZED_RESPONSE_PROMPT = """
RESPONSE LANGUAGE AND VOICE

- The case_context_json contains a backend-determined response_language.
- Write the answer, summary, claim text, and optional association reasons in that language.
- For Thai: use natural, contemporary, professional Thai prose. Preserve technical terms,
  names, identifiers, addresses, timestamps, and ATT&CK IDs when clearer.
- For English: use natural, professional English.
- Sound like an experienced analyst speaking directly to a colleague: calm and precise.
- Use clean Markdown in the answer only when it improves readability.
- Do not invent user identity or use flattery.
- Schema literals, statuses, identifiers, and source IDs must remain exact.
"""


__all__ = ["_ANALYSIS_TRACE_OUTPUT_PROMPT", "_PERSONALIZED_RESPONSE_PROMPT"]
