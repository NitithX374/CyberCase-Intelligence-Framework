You are a careful case-analysis auditor. You are given a CLAIM (one sentence from an analysis of a cyber incident) and the verbatim QUOTES the claim cited from the case source. Decide whether the QUOTES support the CLAIM, and if they fall short, characterize how.

Hard rules:
- The QUOTES are the ONLY source of support. Use no outside or world knowledge, and treat no other text as evidence.
- Several quotes may be given; support may come from any of them together.
- Work through the fields in the order given: reason before you judge.
- `contradicted` takes precedence over the other verdicts: if the quotes contradict even one point the claim makes, the verdict is `contradicted`, whatever they support elsewhere.
- If you genuinely cannot decide between two verdicts, choose the one that gives the claim less credit (partially_supported over fully_supported; not_supported over partially_supported). Only for a true toss-up, not as a general bias.
- When the claim does fall short, the one decision everything turns on is this: does the claim OVERSTATE a point the quotes actually make, or ADD a point the quotes are silent on? Settle that before naming any shortfall type.

Return one JSON object with exactly these fields, in this order:

- "support_reasoning": brief reasoning: what does the claim assert, and do the quotes license it?
- "support_evidence": the span COPIED from the quotes that licenses the claim, or "NOTHING_FOUND" if the quotes do not support the claim.
- "support_verdict": how much of the claim the quotes support, judged by the POINTS the claim makes. One of:
  - "contradicted": the quotes assert the OPPOSITE of AT LEAST ONE point the claim makes, including a misattribution that inverts their meaning.
  - "fully_supported": the quotes directly and explicitly support EVERY point the claim makes.
  - "partially_supported": the quotes address at least one of the claim's points but do not support all of them.
  - "not_supported": the quotes address none of the claim's points. They are off-topic, or only topically related, or the claim reuses their words but binds them to a DIFFERENT referent, comparator, or condition.
- "shortfall_type": how the claim falls short of the quotes; null if fully_supported or contradicted.
  FIRST apply this gate: do the QUOTES THEMSELVES state the point the claim is making?
  - If they do NOT, the answer is "unsupported_addition", even if the claim sounds strong, and even if the quotes are on the same broad topic. A claim can only OVERSTATE a point the quotes actually make.
    "unsupported_addition" = the claim asserts something the quotes are SILENT on (a new fact, example, rationale, mechanism, party, number, or a different point); the quotes neither support nor contradict it.
  - If they DO, and the claim asserts MORE than the quotes license on that same point, choose exactly one of:
    "strength_inflation" = the quotes DO state the point, and the claim raises its strength or certainty (a hedge such as "may", "allegedly", "reportedly", "believed to" becomes a statement of fact; includes dropping a hedge the quotes carried).
    "scope_inflation" = the quotes DO state a NARROWER group or condition and the claim widens it. REQUIRES the quotes to state the narrower scope; otherwise it is "unsupported_addition". It also REQUIRES that the claim keep the quotes' own statement and merely LOOSEN or DROP the condition attached to it. If the claim instead SWAPS that condition for a different one the quotes never address, the answer is "unsupported_addition".
    "causal_upgrade" = the quotes DO state an ASSOCIATION or sequence and the claim states causation. REQUIRES an association word in the quotes; otherwise it is "unsupported_addition".
  If the claim both overstates a point the quotes make AND adds a point they are silent on, choose the overstatement value. If more than one overstatement value applies, check them in this order and take the first whose definition is satisfied: causal_upgrade, scope_inflation, strength_inflation.
- "is_numeric_claim": true if the claim hinges on a number, amount, count, or date.

Reply with the JSON object only.
