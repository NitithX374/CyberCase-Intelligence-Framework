"""Prompts and prompt builders for the Attribute-First Reasoning Pilot.

Implements the semantic contracts for:
1. Attribute Prediction (Step 1 of A1)
2. Direct Zero-Shot Baseline (B0)
3. Attribute-First Generation (Step 2 of A1 with predicted attributes, and A2 with oracle attributes)
"""

from __future__ import annotations

import json
from .contracts import AttributeContract


ATTRIBUTE_PREDICTION_SYSTEM_PROMPT = """You are evaluating only the supplied cybersecurity incident context in relation to the analytical question.

Do not use external cybersecurity knowledge to fill missing facts.

Return JSON only. No markdown fences, no extra text.

Determine:
1. answerability:
   "SUFFICIENT", "INSUFFICIENT", or "CONFLICTING".
   - SUFFICIENT: The supplied context contains enough information to answer the analytical question at the required level.
   - INSUFFICIENT: The requested conclusion cannot be established from the supplied context.
   - CONFLICTING: Relevant supplied evidence provides materially conflicting information that prevents a single unqualified conclusion.

2. question_type:
   "MEANS", "PROGRESSION", "CORRELATION", "IMPACT", "OBJECTIVE", or "OTHER".

3. relevant_evidence_ids:
   Array of sentence IDs (e.g. ["S1", "S3"]) directly useful for answering the analytical question.

4. epistemic_state of the requested conclusion:
   "SUPPORTED", "UNESTABLISHED", or "CONTRADICTED".
   - SUPPORTED: The requested conclusion is supported by the supplied context.
   - UNESTABLISHED: The supplied context neither establishes nor directly disproves the requested conclusion.
   - CONTRADICTED: The requested conclusion is directly contradicted by the supplied context.

5. missing_information:
   Array of strings. If information is insufficient or conflicting, identify only the information necessary to answer the requested question that is absent from the context. If sufficient, provide an empty list [].

Important:
- Lack of support is not contradiction.
- A plausible cybersecurity inference is not established merely because it is technically possible.
- Preserve explicit uncertainty.
- Preserve conflicting evidence.
- Do not invent facts.

JSON Structure:
{
  "answerability": "SUFFICIENT" | "INSUFFICIENT" | "CONFLICTING",
  "question_type": "MEANS" | "PROGRESSION" | "CORRELATION" | "IMPACT" | "OBJECTIVE" | "OTHER",
  "relevant_evidence_ids": ["S1", "S2"],
  "epistemic_state": "SUPPORTED" | "UNESTABLISHED" | "CONTRADICTED",
  "missing_information": ["..."]
}"""


ATTRIBUTE_PREDICTION_USER_TEMPLATE = """Case Context:
{context}

Analytical Question:
{question}"""


DIRECT_BASELINE_SYSTEM_PROMPT = """Answer the analytical cybersecurity question using only the supplied case context.

Do not introduce facts that are not contained in the supplied context.

If the context does not establish the requested conclusion, state that clearly.

If relevant supplied evidence conflicts, preserve that conflict rather than selecting one side without justification.

Give a concise analytical answer."""


DIRECT_BASELINE_USER_TEMPLATE = """Case Context:
{context}

Analytical Question:
{question}"""


ATTRIBUTE_FIRST_SYSTEM_PROMPT = """Answer the analytical cybersecurity question using only the supplied case context.

The following context-analysis attributes have already been determined:
{attributes}

Your answer MUST respect those attributes.

Rules:
- If answerability is INSUFFICIENT, do not produce the requested conclusion as established.
- If answerability is CONFLICTING, explicitly preserve the material conflict.
- If epistemic_state is UNESTABLISHED, do not strengthen the claim.
- If epistemic_state is CONTRADICTED, do not present the requested claim as supported.
- Use only evidence contained in the supplied context.
- Do not add external cybersecurity facts.
- Produce a concise analytical answer."""


ATTRIBUTE_FIRST_USER_TEMPLATE = """Case Context:
{context}

Analytical Question:
{question}"""


def build_attribute_prediction_messages(context: str, question: str) -> list[dict[str, str]]:
    """Build messages payload for attribute prediction."""
    return [
        {"role": "system", "content": ATTRIBUTE_PREDICTION_SYSTEM_PROMPT},
        {"role": "user", "content": ATTRIBUTE_PREDICTION_USER_TEMPLATE.format(context=context, question=question)},
    ]


def build_direct_baseline_messages(context: str, question: str) -> list[dict[str, str]]:
    """Build messages payload for direct zero-shot baseline (B0)."""
    return [
        {"role": "system", "content": DIRECT_BASELINE_SYSTEM_PROMPT},
        {"role": "user", "content": DIRECT_BASELINE_USER_TEMPLATE.format(context=context, question=question)},
    ]


def build_attribute_first_messages(
    context: str, question: str, attributes: AttributeContract | dict
) -> list[dict[str, str]]:
    """Build messages payload for attribute-first generation (A1 and A2)."""
    if isinstance(attributes, AttributeContract):
        attr_dict = attributes.model_dump()
    else:
        attr_dict = attributes

    attr_json = json.dumps(attr_dict, indent=2)
    system_prompt = ATTRIBUTE_FIRST_SYSTEM_PROMPT.format(attributes=attr_json)
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": ATTRIBUTE_FIRST_USER_TEMPLATE.format(context=context, question=question)},
    ]
