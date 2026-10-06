"""
Case Evidence
=============
Which part of the case file a MITRE table row rests on.

A row can be tied to the case file two ways, and both end in a span of the
request's own text:

- **reread** — the table re-read names a technique for a step and copies the
  sentence that reports the step (``table_reread``). This is the model saying
  "this sentence is this technique".
- **retrieval** — retrieval records which sub-queries returned an entity, and
  a sub-query is found in the case file by its own text: the decomposer writes
  each one as a phrase of the incident, often with an English gloss in
  brackets after it. This says only why the entity was looked up: a sub-query
  returns several techniques, and most of them are not what its sentence
  describes. A sub-query the decomposer reworded past finding gives nothing.

The decomposer is not asked where a sub-query comes from. It was tried: told to
copy its source after each query, it stopped writing the English gloss, and
the share of gold techniques retrieval returned fell from .82 to .78 over the
100 real-CTI incidents (evaluation/results/table_evidence.md).

A row lists the re-read's evidence, and retrieval's only when the re-read has
none for it. Judged against the dataset's own cue for each technique on the
100 real-CTI incidents, the re-read had evidence for every gold technique row
and it was the cue's sentence and no other for 98% of them. Retrieval had
evidence for half the rows; the cue's sentence was in it for 86% of those, and
a wrong sentence beside it for a quarter. Listing both would add those wrong
sentences to rows that already have the right one.

Nothing a model wrote is passed on as evidence. A copied sentence is looked up
in the case file and what leaves the service is the slice it was found at, so
``text == case_file[start:end]`` always holds and a consumer can point at it.
A copy that cannot be found is dropped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Iterable, Mapping, Optional

# A model shortens what it copies: it drops a leading connective, trims the
# tail, or respaces Thai text. Whitespace is ignored outright; beyond that the
# copy must still be mostly there, in order, and not stretched over text that
# was never quoted.
_MIN_QUOTE_CHARS = 6
_MIN_MATCHED_SHARE = 0.8
_MAX_STRETCH = 1.25
_EDGE_JUNK = " \t\r\n\"'`“”‘’…."
# "เรียกดูรายละเอียดของระบบปฏิบัติการ (system information discovery)": the
# bracket is the decomposer's gloss, not the incident's words.
_GLOSS = re.compile(r"\s*\([^()]*\)")
# A sub-query that covers this much of the case file is the whole incident
# sent as one query, and points at no sentence.
_MAX_QUERY_SHARE = 0.5
_TECHNIQUE_ID_RE = re.compile(r"^T\d{4}(?:\.\d{3})?$", re.IGNORECASE)

Span = tuple[int, int]


@dataclass(frozen=True)
class CaseSpan:
    """A slice of the case file, and what ties the row to it."""

    start: int
    end: int
    text: str
    basis: str  # "reread" | "retrieval"


def locate(quote: str, case_file: str) -> Optional[Span]:
    """Where ``quote`` is in ``case_file``, as ``(start, end)``; None if it is not.

    Tried in order: the quote as written; the quote with whitespace ignored;
    the longest in-order alignment, accepted when at least 80% of the quote's
    characters are found and the stretch they cover is not much longer than
    the quote.
    """
    quote = (quote or "").strip(_EDGE_JUNK)
    if len(quote) < _MIN_QUOTE_CHARS or not case_file:
        return None

    at = case_file.find(quote)
    if at >= 0:
        return at, at + len(quote)

    # Compare with whitespace removed, keeping each kept character's offset.
    offsets = [i for i, ch in enumerate(case_file) if not ch.isspace()]
    squeezed_file = "".join(case_file[i] for i in offsets)
    squeezed_quote = "".join(ch for ch in quote if not ch.isspace())
    if len(squeezed_quote) < _MIN_QUOTE_CHARS:
        return None

    at = squeezed_file.find(squeezed_quote)
    if at >= 0:
        return offsets[at], offsets[at + len(squeezed_quote) - 1] + 1

    blocks = [
        b
        for b in SequenceMatcher(None, squeezed_file, squeezed_quote, autojunk=False).get_matching_blocks()
        if b.size
    ]
    if not blocks:
        return None
    matched = sum(b.size for b in blocks)
    first, last = blocks[0].a, blocks[-1].a + blocks[-1].size
    if matched < _MIN_MATCHED_SHARE * len(squeezed_quote):
        return None
    if last - first > _MAX_STRETCH * len(squeezed_quote):
        return None
    return offsets[first], offsets[last - 1] + 1


def locate_query(query: str, case_file: str) -> Optional[Span]:
    """Where a retrieval query's own words are in the case file.

    None for the whole incident sent as one query, for a query written in
    other words than the case file's (a broaden round's English rewrite), and
    for one the decomposer reworded past finding.
    """
    span = locate(query, case_file) or locate(_GLOSS.sub("", query or ""), case_file)
    if span and span[1] - span[0] > _MAX_QUERY_SHARE * len(case_file):
        return None
    return span


def merge_spans(spans: Iterable[Span]) -> list[Span]:
    """Spans in case-file order, with overlapping ones joined."""
    merged: list[Span] = []
    for start, end in sorted(set(spans)):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def provenance_key(attack_id: str, stix_id: str) -> str:
    """What retrieval files an entity's sub-queries under: the parent ATT&CK
    ID for a technique or sub-technique, the STIX ID for anything else. The
    same key ``HybridRetriever._technique_key`` gives a hit."""
    if _TECHNIQUE_ID_RE.match(attack_id or ""):
        return attack_id.upper().split(".")[0]
    return stix_id or ""


@dataclass
class CaseEvidence:
    """The spans behind each row of one request's table."""

    case_file: str
    # parent ATT&CK ID → spans the re-read copied for it
    reread: Mapping[str, list[Span]] = field(default_factory=dict)
    # provenance key → where the sub-queries that returned the entity are
    retrieval: Mapping[str, list[Span]] = field(default_factory=dict)

    @classmethod
    def build(
        cls, case_file: str, selection: object = None, rag_result: object = None
    ) -> "CaseEvidence":
        """Gather both kinds of evidence for a request.

        Args:
            case_file: The request's query. Every span is an offset into it.
            selection: The re-read's ``TechniqueSelection``, or None.
            rag_result: The ``GraphRAGResult``; its ``retrieved_by`` says
                which sub-queries returned each entity.
        """
        reread = {
            attack_id: merge_spans(spans)
            for attack_id, spans in (getattr(selection, "spans", None) or {}).items()
            if spans
        }

        retrieved_by = getattr(rag_result, "retrieved_by", None) or {}
        located = {q: locate_query(q, case_file) for queries in retrieved_by.values() for q in queries}
        retrieval: dict[str, list[Span]] = {}
        for key, queries in retrieved_by.items():
            spans = [located[q] for q in queries if located[q]]
            if spans:
                retrieval[key] = merge_spans(spans)
        return cls(case_file=case_file, reread=reread, retrieval=retrieval)

    def for_row(self, attack_id: str, stix_id: str) -> list[CaseSpan]:
        """A row's evidence: what the re-read tied to it, or, when the re-read
        tied nothing to it, where the sub-queries that looked it up are."""
        key = provenance_key(attack_id, stix_id)
        if self.reread.get(key):
            return [self._span(s, "reread") for s in self.reread[key]]
        return [self._span(s, "retrieval") for s in self.retrieval.get(key, [])]

    def _span(self, span: Span, basis: str) -> CaseSpan:
        start, end = span
        return CaseSpan(start=start, end=end, text=self.case_file[start:end], basis=basis)
