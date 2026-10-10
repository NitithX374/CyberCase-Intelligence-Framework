"""A conversation about one case.

The first message is the case file, and it is analysed by the pipeline
``POST /query`` runs — nothing here re-implements the analysis. What this adds
is what comes after it:

    question      → plan (does ATT&CK have to be asked again?) → look up → answer
    added facts   → the case file with the facts appended is analysed again

A question never changes the analysis or the table, and never runs the
pipeline. Only added facts do, and the reader says which of the two a message
is: guessing it from the text would re-run a minute of work, and rewrite the
table, on a misreading.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Callable

from langchain_core.messages import HumanMessage, SystemMessage

from ...config import (
    ATTACK_DOMAIN_FILTER,
    CONVERSATION_HISTORY_TURNS,
    CONVERSATION_LOOKUP_CHARS,
    CONVERSATION_LOOKUP_GRAPH,
    CONVERSATION_LOOKUP_PER_QUERY,
    CONVERSATION_LOOKUP_QUERIES,
    CONVERSATION_PLAN_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    VECTOR_TOP_K,
)
from ...llm_content import invoke_for_text
from ...llm_provider import create_core_chat_model
from ...retrieval.graph_retriever import _EDGE_DISPLAY, SubgraphResult
from ...retrieval.hybrid_retriever import GraphRAGResult
from ..context_builder import build_context
from ..cross_lingual import CrossLingualLayer
from ..query_sanitizer import sanitize_retrieval_query
from .prompts import ANSWER_SYSTEM, PLAN_SYSTEM, answer_prompt, history_text, plan_prompt
from .store import (
    ANALYSIS,
    ANSWER,
    ASSISTANT,
    CASE,
    FACTS,
    QUESTION,
    USER,
    Analysis,
    Conversation,
    Turn,
)

logger = logging.getLogger(__name__)

# The pipeline, as the caller runs it: case text in, analysis out.
Analyse = Callable[[str], Analysis]

# Bounded by ASCII letters and digits rather than \b: Thai is written without
# spaces and its letters count as word characters, so "อธิบายT1105หน่อย" has
# no word boundary on either side of the ID.
_ATTACK_ID = re.compile(
    r"(?<![A-Za-z0-9])(?:TA|DS|T|S|G|M|C)\d{4}(?:\.\d{3})?(?![A-Za-z0-9])", re.IGNORECASE
)
_LOOKUP_YES = re.compile(r"^\s*LOOKUP\s*:\s*yes\b", re.IGNORECASE | re.MULTILINE)
_QUERY_LINE = re.compile(r"^\s*QUERY\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)

# How many entities named by ID are fetched for one message, and how much of
# each one's description is shown.
_MAX_NAMED_IDS = 4
_NAMED_DESCRIPTION_CHARS = 1200
_NAMED_RELATION_NAMES = 15


class ConversationBusy(RuntimeError):
    """A message arrived while the conversation was still answering another."""


def case_with_facts(case_file: str, facts: list[str]) -> str:
    """The text an analysis reads: the case file, then what was added to it."""
    if not facts:
        return case_file
    heading = (
        "ข้อเท็จจริงเพิ่มเติม"
        if CrossLingualLayer.should_respond_in_thai(case_file)
        else "Additional facts"
    )
    return "\n".join([case_file.rstrip(), "", f"{heading}:", *(f"- {f.strip()}" for f in facts)])


def parse_plan(reply: str, message: str) -> list[str]:
    """The search queries a planning reply asks for; none when it asks for none.

    A reply that says yes without a usable query falls back to the message
    itself, so a decision to look something up is never silently dropped.
    """
    if not _LOOKUP_YES.search(reply or ""):
        return []
    queries: list[str] = []
    for raw in _QUERY_LINE.findall(reply):
        query = _clean_query(raw)
        if query and query not in queries:
            queries.append(query)
    if not queries:
        fallback = _clean_query(message)
        queries = [fallback] if fallback else []
    return queries[:CONVERSATION_LOOKUP_QUERIES]


def _clean_query(text: str) -> str:
    """A query as it is embedded: no markdown and no bare IDs (the sanitizer),
    and no gap left inside the brackets an ID was taken out of."""
    query = sanitize_retrieval_query(text)
    return re.sub(r"\s+\)", ")", re.sub(r"\(\s+", "(", query))


def named_ids(message: str) -> list[str]:
    """ATT&CK IDs the reader wrote, in the order written."""
    found = (m.upper() for m in _ATTACK_ID.findall(message or ""))
    return list(dict.fromkeys(found))[:_MAX_NAMED_IDS]


def _relations(subgraph: SubgraphResult) -> list[str]:
    """A named entity's neighbours, one line per relation and kind of neighbour.

    ``SubgraphResult.to_text`` lists everything that uses a technique under a
    single "Used by", and a live answer to "which groups have used T1190"
    then named malware and tools as groups. The kind is known here — every
    neighbour carries its label — so it is kept.
    """
    centre = subgraph.center_node.name
    kinds = {node.name: node.label for node in subgraph.neighbors}
    lists: dict[tuple[str, bool, str], list[str]] = {}
    for edge in subgraph.edges:
        outgoing = edge.source_name == centre
        name = edge.target_name if outgoing else edge.source_name
        names = lists.setdefault((edge.edge_label, outgoing, kinds.get(name, "")), [])
        if name and name not in names:
            names.append(name)

    lines: list[str] = []
    for (edge_label, outgoing, kind), names in lists.items():
        as_source, as_target = _EDGE_DISPLAY.get(edge_label, (edge_label, edge_label))
        head = as_source if outgoing else as_target
        if kind:
            head += f" — {kind}"
        shown = ", ".join(names[:_NAMED_RELATION_NAMES])
        if len(names) > _NAMED_RELATION_NAMES:
            shown += f" (+{len(names) - _NAMED_RELATION_NAMES} more)"
        lines.append(f"  ├── {head}: {shown}")
    return lines


def _row_ids(analysis: Analysis) -> set[str]:
    return {row.technique_id for row in analysis.mitre_table if row.technique_id}


class CaseChat:
    """Runs the turns of a case conversation. Holds no conversation itself."""

    def __init__(self, *, answer_llm: Any, plan_llm: Any, retriever: Any, analyse: Analyse) -> None:
        self.answer_llm = answer_llm
        self.plan_llm = plan_llm
        self.retriever = retriever
        self.analyse = analyse

    @classmethod
    def for_agent(cls, rag_agent: Any, analyse: Analyse) -> "CaseChat":
        """A chat that answers with the agent's own model and retriever."""
        return cls(
            answer_llm=rag_agent.reasoning_llm,
            plan_llm=create_core_chat_model(
                anthropic_model=LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                max_tokens=CONVERSATION_PLAN_MAX_TOKENS,
            ),
            retriever=rag_agent.retriever,
            analyse=analyse,
        )

    # ------------------------------------------------------------------
    # Turns
    # ------------------------------------------------------------------
    def open(self, case_file: str) -> Conversation:
        """Analyse a case file and start the conversation about it."""
        started = time.monotonic()
        analysis = self.analyse(case_file)
        conversation = Conversation(case_file=case_file, analysis=analysis)
        conversation.turns += [
            Turn(USER, CASE, case_file),
            Turn(ASSISTANT, ANALYSIS, analysis.answer, seconds=time.monotonic() - started),
        ]
        return conversation

    def say(self, conversation: Conversation, text: str, kind: str = QUESTION) -> Turn:
        """One message from the reader, and the reply to it.

        Raises:
            ConversationBusy: the conversation is still answering another message.
        """
        if not conversation.busy.acquire(blocking=False):
            raise ConversationBusy(conversation.id)
        try:
            if kind == FACTS:
                return self._add_facts(conversation, text)
            return self._ask(conversation, text)
        finally:
            conversation.busy.release()

    def _add_facts(self, conversation: Conversation, facts: str) -> Turn:
        started = time.monotonic()
        before = _row_ids(conversation.analysis)
        # Analyse first, record after: a run that fails leaves the conversation
        # exactly as it was, without facts the analysis never saw.
        analysis = self.analyse(case_with_facts(conversation.case_file, [*conversation.facts, facts]))
        after = _row_ids(analysis)
        conversation.facts.append(facts)
        conversation.analysis = analysis
        reply = Turn(
            ASSISTANT, ANALYSIS, analysis.answer,
            seconds=time.monotonic() - started,
            rows_added=sorted(after - before),
            rows_removed=sorted(before - after),
        )
        conversation.turns += [Turn(USER, FACTS, facts), reply]
        return reply

    def _ask(self, conversation: Conversation, question: str) -> Turn:
        started = time.monotonic()
        analysis = conversation.analysis
        history = history_text(conversation.turns[-CONVERSATION_HISTORY_TURNS:])

        # Named IDs first: what they fetch is told to the planning call, so it
        # does not spend a search describing an entity already in hand.
        named_text, fetched = self._fetch_named(named_ids(question))
        queries = self._plan(analysis, history, question, fetched)
        searched_text = self._search(queries)
        looked_up = "\n\n".join(filter(None, [named_text, searched_text]))

        answer = invoke_for_text(
            self.answer_llm,
            [
                SystemMessage(content=ANSWER_SYSTEM),
                HumanMessage(content=answer_prompt(analysis, history, question, looked_up)),
            ],
            operation="conversation answer",
        )
        reply = Turn(
            ASSISTANT, ANSWER, answer,
            seconds=time.monotonic() - started,
            # Only what actually reached the answer: a search that failed or
            # found nothing is not something the answer rests on.
            lookup_queries=queries if searched_text else [],
            lookup_ids=fetched,
        )
        conversation.turns += [Turn(USER, QUESTION, question), reply]
        return reply

    # ------------------------------------------------------------------
    # Looking things up — none of it can fail the turn
    # ------------------------------------------------------------------
    def _plan(
        self, analysis: Analysis, history: str, message: str, fetched: list[str]
    ) -> list[str]:
        """Search queries for this message, or none. A planning call that
        fails means no search: the answer still has the case's own material."""
        try:
            reply = invoke_for_text(
                self.plan_llm,
                [
                    SystemMessage(content=PLAN_SYSTEM),
                    HumanMessage(content=plan_prompt(analysis, history, message, fetched)),
                ],
                operation="conversation planning",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("conversation planning failed: %s", exc)
            return []
        return parse_plan(reply, message)

    def _search(self, queries: list[str]) -> str:
        if not queries:
            return ""
        try:
            # Every entity type, not the technique pool the case analysis
            # retrieves from: a follow-up is as likely to be about a
            # mitigation, a group or a tool as about a technique. Twice the
            # quota is fetched because what belongs to another ATT&CK domain
            # is dropped before the quota is applied.
            kept = CONVERSATION_LOOKUP_PER_QUERY * len(queries)
            result = self.retriever.retrieve_multi_quota(
                queries,
                per_query_k=CONVERSATION_LOOKUP_PER_QUERY * 2,
                top_k=VECTOR_TOP_K,
                max_vector=kept * 2,
                max_graph=CONVERSATION_LOOKUP_GRAPH * 2,
                technique_pool=False,
            )
            result = self._in_domain(result)
            result = GraphRAGResult(
                vector_results=result.vector_results[:kept],
                graph_results=result.graph_results[:CONVERSATION_LOOKUP_GRAPH],
            )
            if not result.vector_results:
                return ""
            return build_context(
                result,
                max_context_length=CONVERSATION_LOOKUP_CHARS,
                max_vector=kept,
                max_graph=CONVERSATION_LOOKUP_GRAPH,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("conversation look-up failed: %s", exc)
            return ""

    def _in_domain(self, result: GraphRAGResult) -> GraphRAGResult:
        """The look-up without what belongs to another ATT&CK domain.

        Entity hits come back from the vector search already held to
        ``ATTACK_DOMAIN_FILTER``. Relationship hits are not domain-tagged, and
        with the technique pool off they bring the Mobile matrix's mitigations
        for a technique whose name Enterprise shares — a live question about
        preventing Screen Capture (T1113) was answered with Android guidance.
        A relationship is kept when both its ends are in the domain, a
        subgraph when its centre is.
        """
        graph = getattr(self.retriever, "graph_retriever", None)
        if not ATTACK_DOMAIN_FILTER or graph is None:
            return result
        ends: dict[str, list[str]] = {}
        for hit in result.vector_results:
            metadata = hit.metadata or {}
            if metadata.get("entity_type") == "Relationship":
                ends[hit.stix_id] = [
                    e for e in (metadata.get("source_id"), metadata.get("target_id")) if e
                ]
        centres = [sg.center_node.stix_id for sg in result.graph_results if sg.center_node]
        wanted = sorted({e for pair in ends.values() for e in pair} | set(centres))
        if not wanted:
            return result
        domains = graph.domains_of(wanted)

        def inside(stix_id: str) -> bool:
            return domains.get(stix_id) == ATTACK_DOMAIN_FILTER

        return GraphRAGResult(
            vector_results=[
                hit for hit in result.vector_results
                if hit.stix_id not in ends or all(inside(e) for e in ends[hit.stix_id])
            ],
            graph_results=[
                sg for sg in result.graph_results if sg.center_node and inside(sg.center_node.stix_id)
            ],
        )

    def _fetch_named(self, attack_ids: list[str]) -> tuple[str, list[str]]:
        """The entities the reader named by ID, read straight from the graph.

        A bare ID is a poor search query and an exact key, so it is not
        searched for. Returns the text to show the model and the IDs found.
        """
        graph = getattr(self.retriever, "graph_retriever", None)
        if not attack_ids or graph is None:
            return "", []
        try:
            stix_by_id = graph.stix_ids_for(attack_ids)
            if not stix_by_id:
                return "", []
            stix_ids = list(stix_by_id.values())
            details = graph.entity_details(stix_ids)
            domains = graph.domains_of(stix_ids) if ATTACK_DOMAIN_FILTER else {}
            subgraphs = {
                sg.center_node.stix_id: sg for sg in graph.expand_batch(stix_ids) if sg.center_node
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("conversation ID look-up failed: %s", exc)
            return "", []

        blocks: list[str] = []
        for attack_id, stix_id in stix_by_id.items():
            subgraph = subgraphs.get(stix_id)
            title = f"## {attack_id}"
            relations = ""
            if subgraph:
                centre = subgraph.center_node
                title = f"## {centre.label}: {centre.name} ({centre.attack_id or attack_id})"
                relations = "\n".join(_relations(subgraph))
            # The reader asked for this ID, so it is shown whatever matrix it
            # is from — but labelled, because the Mobile matrix reuses
            # Enterprise technique names under other IDs.
            domain = domains.get(stix_id) or ATTACK_DOMAIN_FILTER
            if ATTACK_DOMAIN_FILTER and domain != ATTACK_DOMAIN_FILTER:
                title += f" — {domain.upper()} ATT&CK, not {ATTACK_DOMAIN_FILTER.capitalize()}"
            description = " ".join((details.get(stix_id, {}).get("description") or "").split())
            if len(description) > _NAMED_DESCRIPTION_CHARS:
                description = description[:_NAMED_DESCRIPTION_CHARS].rstrip() + "…"
            blocks.append("\n".join(filter(None, [title, description, relations])))
        return "\n\n".join(blocks), list(stix_by_id)
