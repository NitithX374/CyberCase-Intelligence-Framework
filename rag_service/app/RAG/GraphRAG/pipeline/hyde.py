"""
HyDE — Hypothetical Document Embeddings
=======================================
Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Labels"
(ACL 2023). Instead of embedding the question, write the document that would
answer it and embed that.

Why it fits this corpus
-----------------------
A sub-query from the decomposer is a sentence from a Thai case file: *what
happened* ("ผู้กระทำสร้างสคริปต์บนเซิร์ฟเวอร์เพื่อสั่งการจากระยะไกล"). The corpus
entry it has to reach is an English encyclopedia entry: *what adversaries may
do* ("Technique: Web Shell. Adversaries may backdoor web servers with web
shells..."). Named-cue steps bridge that gap on the technique name, which both
sides share; described-cue steps have nothing in common but meaning, and on
the real-CTI tier they are retrieved at a fraction of the named rate. A passage
written in the corpus's own register moves the query to the document side.

The risk
--------
The passage carries the model's own guess at the technique. When the guess is
wrong the search is steered to the wrong entry, and the retrieved context
looks like evidence for something the model assumed. That is why each passage
keeps its guessed name and its behavioural description apart: the benchmark
can search with the description alone and measure how much of any gain is the
guess.

One call per incident writes a passage for every sub-query, so the model sees
the whole chain when it writes each one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage

from ..config import LLM_MODEL
from ..llm_content import require_message_text
from ..llm_provider import CoreLlmConfigurationError, create_core_chat_model

_SYSTEM = (
    "You write hypothetical MITRE ATT&CK knowledge-base entries for a retrieval "
    "system. You are given a cybersecurity incident and a numbered list of "
    "search queries, each describing one attacker action from that incident "
    "(queries may be in Thai).\n\n"
    "For EACH query write the ATT&CK Enterprise technique entry that would "
    "describe that action, in English, in the style of the ATT&CK website.\n\n"
    "RULES:\n"
    "1. One line per query, in the same order, formatted exactly as:\n"
    "   <number> | <technique name> | <description>\n"
    "2. <technique name>: the ATT&CK technique or sub-technique name only — no "
    "ID, no parent prefix.\n"
    "3. <description>: 2-3 sentences, starting 'Adversaries may', describing "
    "the behaviour generically as ATT&CK does: what is done, how, and why. "
    "Do NOT mention the victim, dates, places, or anything specific to this "
    "incident.\n"
    "4. Output only those lines — no commentary, no blank lines."
)

_LINE_RE = re.compile(r"^\s*(\d+)\s*[.)]?\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$")


@dataclass
class HydePassage:
    """One hypothetical ATT&CK entry: the model's guess and its description."""

    name: str
    description: str

    def as_document(self) -> str:
        """In the corpus's own entity format: '[Type]: [Name]. [Description]'."""
        return f"Technique: {self.name}. {self.description}"


def _parse(text: str, n: int) -> list[HydePassage | None]:
    """Line ``k | name | description`` → slot k-1. Missing slots stay None."""
    out: list[HydePassage | None] = [None] * n
    for line in text.splitlines():
        m = _LINE_RE.match(line)
        if not m:
            continue
        idx = int(m.group(1)) - 1
        if 0 <= idx < n and out[idx] is None:
            out[idx] = HydePassage(name=m.group(2), description=m.group(3))
    return out


class HydeWriter:
    """LLM step: incident + sub-queries → one hypothetical ATT&CK entry each."""

    def __init__(self) -> None:
        self.llm = None
        try:
            self.llm = create_core_chat_model(
                anthropic_model=LLM_MODEL, temperature=0, max_tokens=4096
            )
        except CoreLlmConfigurationError as exc:
            print(f"[HYDE] No cloud LLM configured: {exc}")

    def write(self, incident: str, sub_queries: list[str]) -> list[HydePassage | None]:
        """One passage per sub-query, in order; None where none was written.

        A None slot is the caller's to fill — searching with the sub-query
        itself is the neutral fallback.
        """
        if not self.llm or not sub_queries:
            return [None] * len(sub_queries)

        numbered = "\n".join(f"{i}. {q}" for i, q in enumerate(sub_queries, 1))
        try:
            resp = self.llm.invoke(
                [
                    SystemMessage(content=_SYSTEM),
                    HumanMessage(
                        content=f"Incident:\n{incident}\n\nQueries:\n{numbered}"
                    ),
                ]
            )
            text = require_message_text(resp, operation="HyDE passage writing")
        except Exception as e:  # network / model error → caller falls back
            print(f"[HYDE] failed ({e}); searching with the sub-queries")
            return [None] * len(sub_queries)
        return _parse(text, len(sub_queries))
