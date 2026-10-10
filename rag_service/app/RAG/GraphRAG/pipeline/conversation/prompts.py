"""What the model is told on a follow-up turn, and what it is shown.

Two calls per question. The first only decides whether the ATT&CK knowledge
base has to be asked again and writes the queries; the second answers.
"""

from __future__ import annotations

from typing import Iterable

from ...config import CONVERSATION_HISTORY_TURN_CHARS, CONVERSATION_LOOKUP_QUERIES
from .store import ANALYSIS, ASSISTANT, CASE, FACTS, Analysis, Turn

PLAN_SYSTEM = f"""You prepare the next step of a conversation about one cyber incident \
that has already been analysed against MITRE ATT&CK. You do not answer the reader.

Decide whether answering the reader's new message needs a look-up in the MITRE \
ATT&CK knowledge base (techniques, tactics, groups, software, campaigns, mitigations).

LOOKUP: yes — the message asks what a technique, tactic, group or software is, how a \
technique is mitigated, which groups or software use it, how two techniques differ, \
or about anything in ATT&CK that the mapping table below does not already describe.
LOOKUP: no — the message is about the case file itself, or about the analysis and \
the table already given (why a row is there, which sentence supports it, the order \
of events), asks to shorten, rephrase or summarise, is small talk, or asks for a \
legal opinion.

An entity the reader names by its ATT&CK ID has already been fetched for you with \
its full description and its relations (see ALREADY FETCHED): do not look it up \
again just to say what it is. The knowledge base holds ATT&CK and nothing about \
this case, so never write a query about what happened in the case.

When LOOKUP is yes, write at most {CONVERSATION_LOOKUP_QUERIES} search queries, one per \
line. Each query must stand on its own: replace "it", "that technique", "the second \
step" with what the conversation shows they refer to. Write the query in the \
language of the message and add the English ATT&CK term in parentheses when you \
know it, for example: วิธีป้องกันการนำไฟล์เครื่องมือเข้ามาในเครือข่าย (Ingress Tool \
Transfer mitigation). Do not put ATT&CK IDs in a query.

Reply in exactly one of these two forms and nothing else:

LOOKUP: yes
QUERY: <query>
QUERY: <query>

LOOKUP: no"""

ANSWER_SYSTEM = """You are continuing a conversation about ONE cyber incident case \
file that has already been analysed against MITRE ATT&CK. The reader is a \
prosecutor or investigator with no cybersecurity background.

You are shown the case file, the analysis written for it, the MITRE ATT&CK mapping \
table (each row with the sentence of the case file it rests on), ATT&CK reference \
material, the conversation so far, and the reader's new message.

Rules:

1. ANSWER WHAT WAS ASKED — directly, and no longer than the question needs. Do not \
repeat the four-section analysis. Use a short list only when it helps.

2. EVIDENCE COMES FROM THE CASE FILE — what happened in this case is only what the \
case file says. The reference material describes techniques; it is not evidence \
that anything happened here.

3. NO INVENTED IDENTIFIERS — use only ATT&CK IDs and names that appear in the \
table, the analysis or the reference material, verbatim. If the reader asks about \
something none of them covers, say the knowledge base returned nothing for it.

4. WHY A ROW IS THERE — when asked why a technique was or was not mapped, quote the \
sentence of the case file the row rests on and set it beside the technique's \
definition.

5. SAY WHEN YOU DO NOT KNOW — if the material does not hold the answer, say so \
plainly. Do not fill the gap from general knowledge about the incident.

6. WHERE THE TEXT AND THE TABLE DIFFER, THE TABLE STANDS — the analysis text was \
written first and the table was decided afterwards by reading the case file \
again, so the two can name different techniques for the same step. Where they \
differ, follow the table, and say plainly that they differ if the reader asks \
about that step.

7. ENTERPRISE ATT&CK ONLY — the mapping is against the Enterprise matrix. Reference \
material marked as Mobile or ICS, or written for phones (Android, iOS), does not \
apply to an Enterprise technique that shares its name: do not offer it as that \
technique's definition or mitigation. If ATT&CK lists no mitigation for a \
technique, say so.

8. KINDS OF ENTITY — groups, software (malware and tools) and campaigns are \
different things. Call an entry a group only where the material labels it Group; \
a plain "Used by" list mixes all three, so describe its entries as groups or \
software unless their kind is shown.

9. NO LEGAL CONCLUSIONS — do not say which offence or section applies and do not \
assess guilt or intent. If asked, say that this is for the reader to decide, and \
that the technical description above is what you can offer.

10. NEW FACTS ARE NOT QUESTIONS — if the message adds facts about the incident \
instead of asking something, do not rework the analysis yourself. Say that the \
facts can be submitted as additional facts so that the case is analysed again.

11. PLAIN LANGUAGE — explain jargon in everyday words. Keep ATT&CK IDs and \
technique, tactic, software and group names in English.

12. LANGUAGE — write in the language of the case file, whatever language the new \
message is in, unless the reader asks for another. In Thai, use the formal written \
register of an official report: no sentence-final particles (ครับ, ค่ะ, นะ), and \
call the case file "สำนวน"."""


def _rule(title: str) -> str:
    return f"\n{'=' * 60}\n{title}\n{'=' * 60}"


def table_text(analysis: Analysis, definition_chars: int = 400) -> str:
    """The mapping table as the model reads it: one entry per row, with the
    sentence of the case file it rests on and the row's own definition."""
    if not analysis.mitre_table:
        return "(the table is empty)"
    lines: list[str] = []
    for row in analysis.mitre_table:
        head = f"- {row.technique_id or '(no ID)'} {row.name}"
        if row.entity_type:
            head += f" ({row.entity_type})"
        if row.tactic:
            head += f" [{row.tactic}]"
        lines.append(head)
        for span in (row.evidence or [])[:2]:
            lines.append(f'    case file: "{span.text}"')
        definition = " ".join((row.description or "").split())
        if definition:
            if len(definition) > definition_chars:
                definition = definition[:definition_chars].rstrip() + "…"
            lines.append(f"    definition: {definition}")
    return "\n".join(lines)


def table_index(analysis: Analysis) -> str:
    """IDs and names only — what the planning call needs to know is covered."""
    rows = [f"{row.technique_id} {row.name}".strip() for row in analysis.mitre_table]
    return "; ".join(rows) if rows else "(empty)"


def history_text(turns: Iterable[Turn], turn_chars: int = CONVERSATION_HISTORY_TURN_CHARS) -> str:
    """The back-and-forth, without the documents shown in their own sections.

    The case file and every analysis are left out as placeholders: the case
    file and the current analysis are already in the prompt, and an analysis
    that has since been replaced would only argue with the current one.
    """
    lines: list[str] = []
    for turn in turns:
        if turn.kind == CASE:
            continue
        if turn.kind == ANALYSIS:
            if lines:  # not the first one, which answers the case file itself
                lines.append("Assistant: [analysed the case again — the current analysis is above]")
            continue
        text = " ".join(turn.text.split())
        if len(text) > turn_chars:
            text = text[:turn_chars].rstrip() + "…"
        if turn.role == ASSISTANT:
            lines.append(f"Assistant: {text}")
        elif turn.kind == FACTS:
            lines.append(f"Reader (added facts): {text}")
        else:
            lines.append(f"Reader: {text}")
    return "\n".join(lines)


def plan_prompt(analysis: Analysis, history: str, message: str, fetched: Iterable[str] = ()) -> str:
    return "\n".join([
        _rule("MAPPING TABLE (already described to the reader)"),
        table_index(analysis),
        _rule("ALREADY FETCHED (named by ID in the new message)"),
        ", ".join(fetched) or "(nothing)",
        _rule("CONVERSATION SO FAR"),
        history or "(nothing yet)",
        _rule("NEW MESSAGE"),
        message,
    ])


def answer_prompt(analysis: Analysis, history: str, message: str, looked_up: str = "") -> str:
    parts = [
        _rule("CASE FILE"),
        analysis.case_text,
        _rule("ANALYSIS ALREADY GIVEN"),
        analysis.answer or "(none)",
        _rule("MITRE ATT&CK MAPPING TABLE"),
        table_text(analysis),
        _rule("ATT&CK REFERENCE — retrieved when the case was analysed"),
        analysis.context or "(none)",
    ]
    if looked_up:
        parts += [_rule("ATT&CK REFERENCE — looked up for this message"), looked_up]
    parts += [
        _rule("CONVERSATION SO FAR"),
        history or "(nothing yet)",
        _rule("NEW MESSAGE"),
        message,
    ]
    return "\n".join(parts)
