"""
MITRE Table Re-read
===================
Decides which Enterprise techniques the MITRE mapping table lists by reading
the case file again, instead of taking them from what the answer cited.

The answer-grounded table (``mitre_table.build_mitre_table``) has two limits.
It can only hold what retrieval returned, and most techniques an answer misses
were never retrieved. And it adds rows the answer did not choose — a parent
because its child was cited, a name that occurs in the text, any vector hit
over the score threshold — which costs precision.

The re-read is two rounds of model calls, ``readings`` calls a round, made side
by side:

1. **Full list.** The case file against every Enterprise parent technique, each
   with its tactics and the first sentence of its definition. A reply names one
   technique per step of the case file.
2. **Shortlist.** The case file against the techniques the answer cites plus
   the ones any full-list reply named, each with its whole definition and the
   names of its sub-techniques. A reply again names one technique per step.

A technique is kept when at least ``votes`` shortlist replies name it. The
model does not repeat itself at temperature 0, which is what makes a vote of
identical calls worth having.

When rows carry evidence (``MITRE_TABLE_EVIDENCE``), each shortlist reply also
copies, for every step, the sentence of the case file that reports it. For a
kept technique those copies are looked up in the case file and the places they
are found at become the row's evidence (``case_evidence``); a copy that is not
in the case file is dropped. The copies make the replies longer, and that is
the whole cost: no call is added. With evidence off the prompt does not ask
for them.

The technique list comes from Neo4j, once per process: the container ships no
STIX bundle, and the graph is what retrieval already answers from.

Nothing here can fail a request. No technique list, a shortlist with nothing
on it, too few readable replies or a vote that keeps nothing all return None,
and the caller builds the answer-grounded table as before.
"""

from __future__ import annotations

import contextvars
import json
import logging
import re
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from ..config import (
    MITRE_TABLE_EVIDENCE,
    MITRE_TABLE_REREAD_READINGS,
    MITRE_TABLE_REREAD_VOTES,
)
from ..llm_content import invoke_for_text
from .case_evidence import Span, locate, merge_spans
from .mitre_table import _ATTACK_ID_PATTERN, _TECHNIQUE_ID_RE, _normalise_description

logger = logging.getLogger(__name__)

# The full-list round shows one sentence a technique, cut here; the shortlist
# round shows the definition up to this many characters.
_INDEX_DEFINITION_CHARS = 220
_SHORTLIST_DEFINITION_CHARS = 900

# Tactics are listed in one fixed order: the matrix's, with the two tactics
# that replaced Defense Evasion where it stood. Neo4j returns them in no order
# at all, the STIX bundle in no consistent one (Collection comes before
# Credential Access on one technique and after it on another), and a prompt
# that changes between two processes cannot be compared.
_TACTIC_ORDER = (
    "reconnaissance",
    "resource-development",
    "initial-access",
    "execution",
    "persistence",
    "privilege-escalation",
    "defense-evasion",
    "stealth",
    "defense-impairment",
    "credential-access",
    "discovery",
    "lateral-movement",
    "collection",
    "command-and-control",
    "exfiltration",
    "impact",
)

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)
_SENTENCE_END = re.compile(r"(?<=[.!?])\s")

INDEX_SYSTEM = """You map a Thai cybercrime case file to MITRE ATT&CK Enterprise techniques. \
The result is a table a prosecutor takes to a technical expert, so every row must be \
something the case file says the offender did.

Work in two steps.
1. List the distinct steps the offender carried out, in the order the case file tells \
them. A sentence that describes one step is ONE step, even when it also says how the \
step was done (the tool, the language a script is written in, the protocol, the account \
used, what was looked at on the way). Count two steps only when the case file joins two \
different things the offender achieved. Leave out what the victim or the investigators \
did and what the offender intended to do next.
2. For each step choose the ONE technique from TECHNIQUES whose definition matches what \
the offender achieved in that step: its purpose, not an incidental detail of how it was \
done. If no technique matches, write "NONE".

TECHNIQUES is the complete list of Enterprise techniques. Use only IDs from it. Never \
list the same technique twice.

Reply with JSON only:
{"steps": [{"step": "<the step, in Thai, a few words>", "technique_id": "<ID or NONE>"}]}"""

_SHORTLIST_TEMPLATE = """You map a Thai cybercrime case file to MITRE ATT&CK Enterprise techniques. \
The result is a table a prosecutor takes to a technical expert, so every row must be \
something the case file says the offender did.

CANDIDATES is a shortlist drawn from the full technique list for this case file. It is \
longer than the answer: several candidates describe a detail of a step and not the step, \
and some do not apply at all. Do not try to use every candidate.

Work in two steps.
1. List the distinct steps the offender carried out, in the order the case file tells \
them. A sentence that describes one step is ONE step, even when it also says how the \
step was done (the tool, the language a script is written in, the protocol, the account \
used, what was looked at on the way). Count two steps only when the case file joins two \
different things the offender achieved.{copy}
2. For each step choose the ONE candidate whose definition matches what the offender \
achieved in that step: its purpose, not an incidental detail of how it was done. If no \
candidate matches, write "NONE".

Use only IDs from CANDIDATES. Never list the same technique twice.

Reply with JSON only:
{{"steps": [{{"step": "<the step, in Thai, a few words>", {field}"technique_id": "<ID or NONE>"}}]}}"""

SHORTLIST_SYSTEM = _SHORTLIST_TEMPLATE.format(copy="", field="")
# The same prompt, asking each step for the sentence that reports it as well.
SHORTLIST_WITH_SENTENCES_SYSTEM = _SHORTLIST_TEMPLATE.format(
    copy=" For each step also copy the sentence of the case file that reports it, word for word.",
    field='"sentence": "<that sentence, copied from the case file>", ',
)


@dataclass(frozen=True)
class TechniqueEntry:
    """One Enterprise parent technique as the re-read shows it to the model."""

    attack_id: str
    stix_id: str
    name: str
    description: str  # normalised, as a table row carries it
    tactics: tuple[str, ...]  # shortnames, matrix order
    tactic_names: tuple[str, ...]  # display names, same order
    sub_names: tuple[str, ...]

    @property
    def definition(self) -> str:
        """The first sentence of the description."""
        return _SENTENCE_END.split(self.description, maxsplit=1)[0][:_INDEX_DEFINITION_CHARS]


@dataclass(frozen=True)
class TechniqueSelection:
    """What a re-read decided: the techniques it keeps, out of the ones it read."""

    kept: tuple[TechniqueEntry, ...]
    considered: frozenset[str]  # every parent ID on the full list
    # kept parent ID → where in the case file the replies that named it found
    # the step, as (start, end) offsets
    spans: Mapping[str, tuple[Span, ...]] = field(default_factory=dict)

    def ruling(self, attack_id: str) -> Optional[bool]:
        """Whether a row with this ID belongs in the table.

        None for anything the re-read did not read — another domain's
        technique, software, a group — which the caller decides as before. A
        sub-technique is ruled on through its parent.
        """
        parent = (attack_id or "").upper().split(".")[0]
        if parent not in self.considered:
            return None
        return any(entry.attack_id == parent for entry in self.kept)


def build_catalogue(rows: list[dict]) -> tuple[TechniqueEntry, ...]:
    """The full technique list, from ``GraphRetriever.enterprise_techniques``."""
    entries = []
    for row in rows:
        attack_id = (row.get("attack_id") or "").upper()
        if not attack_id or not row.get("name"):
            continue
        tactics = sorted(
            (
                (t.get("shortname") or "", t.get("name") or "")
                for t in row.get("tactics") or []
                if t.get("shortname")
            ),
            key=lambda t: (_tactic_rank(t[0]), t[0]),
        )
        entries.append(
            TechniqueEntry(
                attack_id=attack_id,
                stix_id=row.get("stix_id") or "",
                name=row["name"],
                description=_normalise_description(row.get("description")),
                tactics=tuple(short for short, _ in tactics),
                tactic_names=tuple(name or short for short, name in tactics),
                sub_names=tuple(sorted(filter(None, row.get("sub_names") or []))),
            )
        )
    return tuple(sorted(entries, key=lambda e: e.attack_id))


def _tactic_rank(shortname: str) -> int:
    return _TACTIC_ORDER.index(shortname) if shortname in _TACTIC_ORDER else len(_TACTIC_ORDER)


def index_prompt(case_file: str, catalogue: tuple[TechniqueEntry, ...]) -> str:
    lines = [
        f"{e.attack_id} {e.name} [{', '.join(e.tactics)}]: {e.definition}" for e in catalogue
    ]
    return f"CASE FILE\n{case_file}\n\nTECHNIQUES\n" + "\n".join(lines)


def shortlist_prompt(case_file: str, shortlist: list[TechniqueEntry]) -> str:
    blocks = []
    for e in shortlist:
        text = e.description
        if len(text) > _SHORTLIST_DEFINITION_CHARS:
            text = text[:_SHORTLIST_DEFINITION_CHARS].rsplit(" ", 1)[0] + "…"
        block = f"{e.attack_id} {e.name} [{', '.join(e.tactics)}]\n{text}"
        if e.sub_names:
            block += "\nIncludes: " + "; ".join(e.sub_names) + "."
        blocks.append(block)
    return f"CASE FILE\n{case_file}\n\nCANDIDATES\n\n" + "\n\n".join(blocks)


def cited_parent_ids(answer: str) -> set[str]:
    """Parent technique IDs an answer cites, by ID."""
    cited = (m.upper() for m in _ATTACK_ID_PATTERN.findall(answer or ""))
    return {c.split(".")[0] for c in cited if _TECHNIQUE_ID_RE.match(c)}


def reply_ids(raw: str, allowed: set[str]) -> Optional[list[str]]:
    """Parent IDs a reply names, in its order. None when it cannot be read."""
    steps = reply_steps(raw, allowed)
    return None if steps is None else [attack_id for attack_id, _ in steps]


def reply_steps(raw: str, allowed: set[str]) -> Optional[list[tuple[str, str]]]:
    """``(parent ID, copied sentence)`` for each technique a reply names, in
    its order. None when the reply cannot be read.

    An unreadable reply and a reply that names nothing are different things:
    the first is a call that failed, the second is a reading that found no
    technique, and only the second gets a vote. The sentence is "" when the
    reply gave none.
    """
    match = _JSON_BLOCK.search(raw or "")
    if not match:
        return None
    try:
        reply = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    steps = reply.get("steps") if isinstance(reply, dict) else None
    if not isinstance(steps, list):
        return None
    named: list[tuple[str, str]] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        attack_id = str(step.get("technique_id") or "").strip().upper().split(".")[0]
        if attack_id in allowed and all(attack_id != seen for seen, _ in named):
            named.append((attack_id, str(step.get("sentence") or "")))
    return named


class TableReread:
    """The two rounds, for one process: holds the model and the technique list."""

    def __init__(
        self,
        llm: Any,
        list_techniques: Callable[[], list[dict]],
        readings: int = MITRE_TABLE_REREAD_READINGS,
        votes: int = MITRE_TABLE_REREAD_VOTES,
        copy_sentences: bool = MITRE_TABLE_EVIDENCE,
    ) -> None:
        self._llm = llm
        self._list_techniques = list_techniques
        self._shortlist_system = (
            SHORTLIST_WITH_SENTENCES_SYSTEM if copy_sentences else SHORTLIST_SYSTEM
        )
        self.readings = max(1, readings)
        self.votes = max(1, min(votes, self.readings))
        self._catalogue: tuple[TechniqueEntry, ...] = ()
        self._catalogue_lock = threading.Lock()

    def catalogue(self) -> tuple[TechniqueEntry, ...]:
        """The full list, read from the graph on first use.

        Built whole and then published, under a lock: requests arrive on
        several worker threads, and a list filled in place would reach the
        prompt half-built or several times over. A failed read is not kept, so
        the next request asks again.
        """
        with self._catalogue_lock:
            if not self._catalogue:
                try:
                    self._catalogue = build_catalogue(self._list_techniques())
                except Exception as exc:  # noqa: BLE001
                    logger.warning("MITRE table re-read: technique list unavailable: %s", exc)
            return self._catalogue

    def select(
        self, case_file: str, answer: str, trace: Optional[dict] = None
    ) -> Optional[TechniqueSelection]:
        """Read the case file again and return the techniques to list.

        Args:
            case_file: The incident text the agent was asked about.
            answer: The agent's answer. Only its cited technique IDs are used,
                to put them on the shortlist.
            trace: A dict to fill with what each round returned, for a caller
                that shows the re-read's work. ``outcome`` is ``"decided"`` or
                the reason there is no selection; ``cited``, ``full_list`` (the
                IDs each readable reply named), ``shortlist``, ``names`` (of
                the shortlisted techniques), ``readings`` (as ``full_list``,
                for the shortlist round), ``votes``, ``kept``, ``quotes``
                (the sentences the replies copied for each kept technique) and
                ``spans`` (where those were found in the case file) are
                present as far as the re-read got. Nothing reads it back.

        Returns:
            The selection, or None when the re-read could not decide and the
            answer-grounded table should stand.
        """
        trace = trace if trace is not None else {}
        trace.update(asked=self.readings, needed=self.votes)

        catalogue = self.catalogue()
        if not catalogue:
            trace["outcome"] = "no technique list"
            return None
        if not (case_file or "").strip():
            trace["outcome"] = "no case file"
            return None
        by_id = {e.attack_id: e for e in catalogue}

        proposed = cited_parent_ids(answer)
        trace["cited"] = sorted(proposed & set(by_id))
        trace["full_list"] = []
        for raw in self._ask(INDEX_SYSTEM, index_prompt(case_file, catalogue), "full list"):
            named = reply_ids(raw, set(by_id))
            if named is not None:
                trace["full_list"].append(named)
                proposed.update(named)
        shortlist = [by_id[i] for i in sorted(proposed) if i in by_id]
        trace["shortlist"] = [e.attack_id for e in shortlist]
        trace["names"] = {e.attack_id: e.name for e in shortlist}
        if not shortlist:
            logger.warning("MITRE table re-read: nothing on the shortlist")
            trace["outcome"] = "nothing on the shortlist"
            return None

        allowed = {e.attack_id for e in shortlist}
        replies = self._ask(
            self._shortlist_system, shortlist_prompt(case_file, shortlist), "shortlist"
        )
        read = [steps for steps in (reply_steps(raw, allowed) for raw in replies) if steps is not None]
        readings = [[attack_id for attack_id, _ in steps] for steps in read]
        trace["readings"] = readings
        if len(readings) < self.votes:
            logger.warning(
                "MITRE table re-read: %d of %d shortlist replies readable, %d needed",
                len(readings),
                self.readings,
                self.votes,
            )
            trace["outcome"] = "too few readable replies"
            return None

        counts = Counter(i for ids in readings for i in ids)
        kept = tuple(by_id[i] for i in sorted(counts) if counts[i] >= self.votes)
        trace.update(votes=dict(counts), kept=[e.attack_id for e in kept])
        if not kept:
            logger.warning("MITRE table re-read: the vote kept no technique")
            trace["outcome"] = "the vote kept nothing"
            return None

        # Where each kept technique's step is in the case file, from every
        # reply that named it. A sentence the model reworded past finding is
        # left out: evidence is a place in the case file or nothing.
        spans: dict[str, tuple[Span, ...]] = {}
        for entry in kept:
            found = [
                locate(sentence, case_file)
                for steps in read
                for attack_id, sentence in steps
                if attack_id == entry.attack_id
            ]
            spans[entry.attack_id] = tuple(merge_spans(span for span in found if span))
        trace["quotes"] = {
            entry.attack_id: [s for steps in read for a, s in steps if a == entry.attack_id and s]
            for entry in kept
        }
        trace["spans"] = {attack_id: [list(span) for span in found] for attack_id, found in spans.items()}
        trace["outcome"] = "decided"
        return TechniqueSelection(kept=kept, considered=frozenset(by_id), spans=spans)

    def _ask(self, system: str, user: str, round_name: str) -> list[str]:
        """The same prompt ``readings`` times, side by side. A call that raises
        is one reply fewer, not a failed round."""
        messages = [SystemMessage(content=system), HumanMessage(content=user)]

        def one(_: int) -> Optional[str]:
            try:
                return invoke_for_text(
                    self._llm, messages, operation=f"MITRE table re-read ({round_name})"
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("MITRE table re-read: a %s call failed: %s", round_name, exc)
                return None

        # Each call runs in a copy of the caller's context, so LangChain
        # callbacks the caller is running under (tracing, token counts) see
        # the calls made on these threads as well.
        contexts = [contextvars.copy_context() for _ in range(self.readings)]
        with ThreadPoolExecutor(max_workers=self.readings) as pool:
            replies = pool.map(lambda numbered: numbered[1].run(one, numbered[0]), enumerate(contexts))
            return [raw for raw in replies if raw is not None]
