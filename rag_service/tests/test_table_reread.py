"""
Unit Tests for the MITRE table re-read
======================================
The technique list reaches the prompt once however many threads ask for it.
A shortlist is what the answer cites plus what the full-list replies name, and
a technique is kept on a vote of the shortlist replies. Whatever goes wrong —
no list, a call that raises, a reply that cannot be read, a vote that keeps
nothing — the re-read returns None and the table stays answer-grounded.
In the table, the selection decides the Enterprise technique rows and no others.
"""

import json
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.pipeline.mitre_table import build_mitre_table
from RAG.GraphRAG.pipeline.table_reread import (
    INDEX_SYSTEM,
    SHORTLIST_SYSTEM,
    TableReread,
    TechniqueSelection,
    build_catalogue,
    cited_parent_ids,
    index_prompt,
    reply_ids,
    shortlist_prompt,
)
from RAG.GraphRAG.retrieval.graph_retriever import GraphNode, GraphRetriever, SubgraphResult
from RAG.GraphRAG.retrieval.hybrid_retriever import GraphRAGResult
from RAG.GraphRAG.retrieval.vector_retriever import VectorResult
from routers import rag as rag_router

_TACTICS = {
    "initial-access": "Initial Access",
    "execution": "Execution",
    "persistence": "Persistence",
    "stealth": "Stealth",
    "impact": "Impact",
}


def _row(attack_id, name, tactics, description=None, subs=()):
    return {
        "stix_id": f"attack-pattern--{attack_id}",
        "attack_id": attack_id,
        "name": name,
        "description": description or f"Adversaries may use {name}. A second sentence.",
        "tactics": [{"shortname": t, "name": _TACTICS[t]} for t in tactics],
        "sub_names": list(subs),
    }


_ROWS = [
    _row("T1566", "Phishing", ["initial-access"], subs=["Spearphishing Link", "Spearphishing Attachment"]),
    _row("T1486", "Data Encrypted for Impact", ["impact"]),
    _row("T1078", "Valid Accounts", ["stealth", "initial-access", "persistence"]),
    _row("T1059", "Command and Scripting Interpreter", ["execution"], subs=["PowerShell"]),
]


def _steps(*ids):
    return json.dumps({"steps": [{"step": "ขั้นตอน", "technique_id": i} for i in ids]})


class _Model:
    """Answers each round from its own script; a script entry that is an
    exception is raised instead."""

    def __init__(self, full_list, shortlist):
        self._scripts = {INDEX_SYSTEM: list(full_list), SHORTLIST_SYSTEM: list(shortlist)}
        self.prompts = {INDEX_SYSTEM: [], SHORTLIST_SYSTEM: []}
        self._lock = threading.Lock()

    def invoke(self, messages):
        system, user = messages[0].content, messages[1].content
        with self._lock:
            self.prompts[system].append(user)
            reply = self._scripts[system].pop(0)
        if isinstance(reply, Exception):
            raise reply
        return SimpleNamespace(text=reply, content=reply)


def _reread(full_list, shortlist, rows=_ROWS):
    model = _Model(full_list, shortlist)
    return TableReread(model, lambda: rows, readings=3, votes=2), model


# ── the technique list ────────────────────────────────────────────────────────


def test_catalogue_is_sorted_and_keeps_tactics_in_one_order():
    catalogue = build_catalogue(list(reversed(_ROWS)))

    assert [e.attack_id for e in catalogue] == ["T1059", "T1078", "T1486", "T1566"]
    valid_accounts = catalogue[1]
    assert valid_accounts.tactics == ("initial-access", "persistence", "stealth")
    assert valid_accounts.tactic_names == ("Initial Access", "Persistence", "Stealth")
    assert valid_accounts.definition == "Adversaries may use Valid Accounts."
    assert catalogue[3].sub_names == ("Spearphishing Attachment", "Spearphishing Link")


def test_catalogue_skips_a_node_without_an_id_or_a_name():
    rows = [*_ROWS, _row("", "Nameless ID", ["impact"]), {**_row("T9999", "x", ["impact"]), "name": ""}]

    assert len(build_catalogue(rows)) == len(_ROWS)


def test_the_list_is_read_once_when_several_requests_arrive_together():
    calls = []

    def slow_list():
        calls.append(1)
        time.sleep(0.05)
        return _ROWS

    reread = TableReread(_Model([], []), slow_list)
    seen = []
    threads = [threading.Thread(target=lambda: seen.append(reread.catalogue())) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(calls) == 1
    assert all(len(catalogue) == len(_ROWS) for catalogue in seen)
    # Each technique is in the prompt exactly once.
    prompt = index_prompt("สำนวน", reread.catalogue())
    assert [prompt.count(f"\n{r['attack_id']} ") for r in _ROWS] == [1] * len(_ROWS)


def test_a_failed_read_of_the_list_is_asked_again_next_time():
    attempts = []

    def flaky_list():
        attempts.append(1)
        if len(attempts) == 1:
            raise ConnectionError("neo4j unreachable")
        return _ROWS

    model = _Model([_steps("T1566")] * 3, [_steps("T1566")] * 3)
    reread = TableReread(model, flaky_list)

    assert reread.select("สำนวน", "") is None
    assert model.prompts[INDEX_SYSTEM] == []  # no list, so no call was paid for
    assert reread.select("สำนวน", "") is not None


# ── prompts and replies ───────────────────────────────────────────────────────


def test_index_prompt_shows_one_sentence_and_the_shortlist_the_whole_definition():
    catalogue = build_catalogue(_ROWS)

    assert index_prompt("สำนวน", catalogue).endswith(
        "\nT1566 Phishing [initial-access]: Adversaries may use Phishing."
    )
    block = shortlist_prompt("สำนวน", [catalogue[3]])
    assert "T1566 Phishing [initial-access]\nAdversaries may use Phishing. A second sentence." in block
    assert block.endswith("Includes: Spearphishing Attachment; Spearphishing Link.")


def test_shortlist_definition_is_cut_on_a_word():
    long = build_catalogue([_row("T1566", "Phishing", ["initial-access"], description="word " * 400)])

    body = shortlist_prompt("สำนวน", list(long)).split("\n")[-1]
    assert body.endswith("word…") and len(body) <= 901


def test_cited_parent_ids_reads_ids_written_against_thai_text():
    answer = "ผู้กระทำผิดใช้T1566.002 และ T1078 ผ่านมัลแวร์ S0002 ในกลยุทธ์ TA0001"

    assert cited_parent_ids(answer) == {"T1566", "T1078"}


def test_reply_ids_rolls_up_keeps_order_and_ignores_what_is_not_allowed():
    raw = "```json\n" + _steps("t1566.002", "NONE", "T1486", "T1566", "T4242") + "\n```"

    assert reply_ids(raw, {"T1566", "T1486"}) == ["T1566", "T1486"]


def test_a_reply_that_names_nothing_is_a_reading_and_a_broken_one_is_not():
    assert reply_ids(_steps("NONE"), {"T1566"}) == []
    assert reply_ids('{"steps": []}', {"T1566"}) == []
    assert reply_ids("ขออภัย ไม่สามารถตอบได้", {"T1566"}) is None
    assert reply_ids('{"steps": [', {"T1566"}) is None
    assert reply_ids('{"techniques": ["T1566"]}', {"T1566"}) is None


# ── the two rounds ────────────────────────────────────────────────────────────


def test_shortlist_is_what_the_answer_cites_plus_what_the_full_list_named():
    reread, model = _reread(
        full_list=[_steps("T1566"), _steps("T1566", "T1486"), _steps("NONE")],
        shortlist=[_steps("T1566", "T1486")] * 3,
    )

    reread.select("สำนวนคดี", "คำตอบอ้าง T1078.004")

    assert len(model.prompts[INDEX_SYSTEM]) == 3
    shortlist = model.prompts[SHORTLIST_SYSTEM][0]
    assert shortlist.startswith("CASE FILE\nสำนวนคดี\n\nCANDIDATES\n\n")
    assert [i for i in ("T1059", "T1078", "T1486", "T1566") if f"\n{i} " in shortlist] == [
        "T1078",
        "T1486",
        "T1566",
    ]


def test_a_technique_is_kept_on_two_of_three_shortlist_replies():
    reread, _ = _reread(
        full_list=[_steps("T1566", "T1486")] * 3,
        shortlist=[_steps("T1566", "T1486"), _steps("T1566", "T1078"), _steps("T1566")],
    )

    selection = reread.select("สำนวน", "คำตอบอ้าง T1078")

    assert [e.attack_id for e in selection.kept] == ["T1566"]
    assert selection.ruling("T1566") is True
    assert selection.ruling("T1566.002") is True  # through its parent
    assert selection.ruling("T1078") is False  # read, and not kept
    assert selection.ruling("T1417") is None  # not on the list: another domain
    assert selection.ruling("S0002") is None
    assert selection.ruling("") is None


def test_a_technique_retrieval_never_returned_can_be_kept():
    reread, _ = _reread(
        full_list=[_steps("T1486")] * 3, shortlist=[_steps("T1486")] * 3
    )

    selection = reread.select("สำนวน", "คำตอบไม่ได้อ้างเทคนิคใด")

    assert [e.attack_id for e in selection.kept] == ["T1486"]


def test_a_failed_full_list_round_leaves_the_answers_techniques_to_be_read():
    reread, model = _reread(
        full_list=[TimeoutError("slow")] * 3, shortlist=[_steps("T1078")] * 3
    )

    selection = reread.select("สำนวน", "คำตอบอ้าง T1078")

    assert [e.attack_id for e in selection.kept] == ["T1078"]
    assert "\nT1566 " not in model.prompts[SHORTLIST_SYSTEM][0]


def test_two_readable_replies_still_decide_and_must_agree():
    reread, _ = _reread(
        full_list=[_steps("T1566", "T1486")] * 3,
        shortlist=[_steps("T1566", "T1486"), TimeoutError("slow"), _steps("T1566")],
    )

    assert [e.attack_id for e in reread.select("สำนวน", "").kept] == ["T1566"]


def test_one_readable_reply_is_not_a_vote():
    reread, _ = _reread(
        full_list=[_steps("T1566")] * 3,
        shortlist=[_steps("T1566"), "ไม่ใช่ JSON", TimeoutError("slow")],
    )

    assert reread.select("สำนวน", "") is None


def test_no_selection_when_nothing_is_proposed_or_nothing_is_kept():
    nothing_proposed, model = _reread(full_list=[_steps("NONE")] * 3, shortlist=[])
    assert nothing_proposed.select("สำนวน", "คำตอบไม่ได้อ้างเทคนิคใด") is None
    assert model.prompts[SHORTLIST_SYSTEM] == []

    nothing_kept, _ = _reread(
        full_list=[_steps("T1566")] * 3,
        shortlist=[_steps("T1566"), _steps("NONE"), _steps("NONE")],
    )
    assert nothing_kept.select("สำนวน", "") is None


def test_the_trace_shows_each_round_and_why_there_is_no_selection():
    reread, _ = _reread(
        full_list=[_steps("T1566"), "ไม่ใช่ JSON", _steps("T1566", "T1486")],
        shortlist=[_steps("T1566", "T1486"), _steps("T1566", "T1078"), _steps("T1566")],
    )
    trace = {}

    reread.select("สำนวน", "คำตอบอ้าง T1078.004 และ T1417", trace)

    assert trace == {
        "asked": 3,
        "needed": 2,
        "cited": ["T1078"],  # T1417 is not on the list
        "full_list": [["T1566"], ["T1566", "T1486"]],  # the unreadable reply is not a reading
        "shortlist": ["T1078", "T1486", "T1566"],
        "readings": [["T1566", "T1486"], ["T1566", "T1078"], ["T1566"]],
        "votes": {"T1566": 3, "T1486": 1, "T1078": 1},
        "kept": ["T1566"],
        "outcome": "decided",
    }

    gave_up, _ = _reread(full_list=[_steps("T1566")] * 3, shortlist=[_steps("T1566"), "x", "y"])
    trace = {}
    assert gave_up.select("สำนวน", "", trace) is None
    assert trace["outcome"] == "too few readable replies"
    assert "kept" not in trace


def test_calls_report_to_callbacks_the_caller_is_running_under():
    import contextvars

    marker = contextvars.ContextVar("marker", default="unset")
    seen = []

    class _Model:
        def invoke(self, messages):
            seen.append(marker.get())
            return SimpleNamespace(text=_steps("T1566"), content=_steps("T1566"))

    marker.set("caller")
    TableReread(_Model(), lambda: _ROWS).select("สำนวน", "")

    assert seen == ["caller"] * 6


def test_no_call_is_made_for_an_empty_case_file():
    reread, model = _reread(full_list=[], shortlist=[])

    assert reread.select("   ", "คำตอบอ้าง T1566") is None
    assert model.prompts[INDEX_SYSTEM] == []


# ── the table ─────────────────────────────────────────────────────────────────


def _hit(name, label, attack_id, score, stix_id=None):
    return VectorResult(
        document=f"{label}: {name}. Retrieved description of {name}.",
        metadata={"entity_type": "Node", "node_label": label, "name": name, "attack_id": attack_id},
        score=score,
        stix_id=stix_id or f"sid-{attack_id}",
    )


def _selection(*kept_ids):
    catalogue = build_catalogue(_ROWS)
    return TechniqueSelection(
        kept=tuple(e for e in catalogue if e.attack_id in kept_ids),
        considered=frozenset(e.attack_id for e in catalogue),
    )


def _table(result, answer, *kept_ids, **kwargs):
    rows = build_mitre_table(result, answer, selection=_selection(*kept_ids), **kwargs)
    return {r.technique_id: r for r in rows}


def test_a_kept_technique_retrieval_never_returned_is_a_row_from_its_own_node():
    result = GraphRAGResult(vector_results=[_hit("Phishing", "Technique", "T1566", 0.9)], graph_results=[])

    rows = _table(result, "คำตอบอ้าง T1566", "T1566", "T1486")

    added = rows["T1486"]
    assert (added.source, added.score, added.relevance) == ("graph", None, "retrieved_only")
    assert added.entity_type == "Technique"
    assert added.tactic == "Impact"
    assert added.description == "Adversaries may use Data Encrypted for Impact. A second sentence."
    assert added.mitre_url == "https://attack.mitre.org/techniques/T1486/"
    assert (rows["T1566"].source, rows["T1566"].relevance) == ("vector", "cited_in_answer")


def test_an_added_row_asks_its_own_node_for_tactic_and_description():
    result = GraphRAGResult(vector_results=[], graph_results=[])
    asked = []

    def lookup(stix_ids):
        asked.extend(stix_ids)
        return {"attack-pattern--T1486": {"description": "From the node.", "tactics": ["Impact"]}}

    rows = _table(result, "คำตอบ", "T1486", entity_details=lookup)

    assert asked == ["attack-pattern--T1486"]
    assert (rows["T1486"].description, rows["T1486"].tactic) == ("From the node.", "Impact")


def test_a_technique_the_reread_did_not_keep_is_not_a_row_even_when_cited():
    result = GraphRAGResult(
        vector_results=[
            _hit("Phishing", "Technique", "T1566", 0.9),
            _hit("Valid Accounts", "Technique", "T1078", 0.8),  # cited, not kept
            _hit("Command and Scripting Interpreter", "Technique", "T1059", 0.95),  # over the threshold
        ],
        graph_results=[],
    )
    answer = "คำตอบอ้าง T1566 และ T1078"

    assert set(_table(result, answer, "T1566")) == {"T1566"}
    assert {r.technique_id for r in build_mitre_table(result, answer)} == {"T1566", "T1078", "T1059"}


def test_a_sub_technique_is_a_row_only_when_cited_and_its_parent_is_kept():
    result = GraphRAGResult(
        vector_results=[
            _hit("Spearphishing Link", "Subtechnique", "T1566.002", 0.9),
            _hit("Spearphishing Attachment", "Subtechnique", "T1566.001", 0.9),  # not cited
            _hit("PowerShell", "Subtechnique", "T1059.001", 0.9),  # cited, parent not kept
        ],
        graph_results=[],
    )

    rows = _table(result, "คำตอบอ้าง T1566.002 และ T1059.001", "T1566")

    assert set(rows) == {"T1566", "T1566.002"}
    # The parent was cited through its child, as the answer-grounded table counts it.
    assert rows["T1566"].relevance == "cited_in_answer"


def test_rows_that_are_not_techniques_follow_the_old_rules():
    result = GraphRAGResult(
        vector_results=[
            _hit("Mimikatz", "Software", "S0002", 0.2),  # cited
            _hit("Cobalt Strike", "Software", "S0154", 0.9),  # over the threshold
            _hit("PsExec", "Software", "S0029", 0.2),  # neither
        ],
        graph_results=[
            SubgraphResult(
                center_node=GraphNode("g1", "APT28", "Group", "G0007"), neighbors=[], edges=[]
            )
        ],
    )

    rows = _table(result, "คำตอบอ้าง S0002", "T1566")

    assert set(rows) == {"T1566", "S0002", "S0154"}


def test_another_domains_technique_is_a_row_only_when_its_id_is_cited():
    # The mobile matrix reuses Enterprise names; these are mobile techniques.
    result = GraphRAGResult(
        vector_results=[
            _hit("Input Capture", "Technique", "T1417", 0.2),  # cited by ID
            _hit("Phishing", "Technique", "T1660", 0.9),  # name in the answer, over the threshold
        ],
        graph_results=[
            SubgraphResult(
                center_node=GraphNode("m1", "Screen Capture", "Technique", "T1513"),
                neighbors=[],
                edges=[],
            )
        ],
    )
    answer = "คำตอบอ้าง Phishing (T1566), Screen Capture (T1113) และ T1417"

    assert set(_table(result, answer, "T1566")) == {"T1566", "T1417"}
    # Without a re-read the name is enough, as it always was.
    assert {r.technique_id for r in build_mitre_table(result, answer)} == {"T1417", "T1660", "T1513"}


def test_selected_rows_come_before_rows_kept_on_score_alone():
    result = GraphRAGResult(
        vector_results=[_hit("Cobalt Strike", "Software", "S0154", 0.99)], graph_results=[]
    )

    rows = build_mitre_table(result, "คำตอบ", selection=_selection("T1486"))

    assert [r.technique_id for r in rows] == ["T1486", "S0154"]


# ── the graph query and the route ─────────────────────────────────────────────


def test_enterprise_techniques_asks_for_parents_of_one_domain_in_one_query():
    log = []

    class _Session:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def run(self, query, **params):
            log.append(getattr(query, "text", str(query)))
            return [_ROWS[0]]

    graph = GraphRetriever.__new__(GraphRetriever)  # no Neo4j
    graph.driver = SimpleNamespace(session=_Session)

    assert graph.enterprise_techniques() == [_ROWS[0]]
    assert len(log) == 1
    assert "(t:Technique {domain: 'enterprise'})" in log[0]
    assert "(s:Subtechnique)-[:SUBTECHNIQUE_OF]->(t)" in log[0]


def _agent(reread, answer="คำตอบอ้าง T1566"):
    result = GraphRAGResult(vector_results=[_hit("Phishing", "Technique", "T1566", 0.9)], graph_results=[])
    return SimpleNamespace(
        query=lambda query, verbose: SimpleNamespace(answer=answer, context="ctx", graphrag_result=result),
        table_reread=reread,
    )


def test_the_route_builds_the_table_from_the_rereads_selection():
    asked = []

    class _Reread:
        def select(self, case_file, answer, trace=None):
            asked.append((case_file, answer))
            return _selection("T1486")

    _, table = rag_router._run_pipeline(_agent(_Reread()), "สำนวนคดี")

    assert asked == [("สำนวนคดี", "คำตอบอ้าง T1566")]
    assert [r.technique_id for r in table] == ["T1486"]


def test_a_reread_that_raises_or_gives_up_leaves_the_answer_grounded_table():
    class _Broken:
        def select(self, case_file, answer, trace=None):
            raise RuntimeError("model unreachable")

    class _GivesUp:
        def select(self, case_file, answer, trace=None):
            return None

    for reread in (_Broken(), _GivesUp(), None):
        _, table = rag_router._run_pipeline(_agent(reread), "สำนวนคดี")
        assert [r.technique_id for r in table] == ["T1566"]


def test_the_reread_is_not_run_without_an_answer():
    class _MustNotRun:
        def select(self, case_file, answer, trace=None):
            raise AssertionError("re-read called without an answer")

    _, table = rag_router._run_pipeline(_agent(_MustNotRun(), answer=""), "สำนวนคดี")

    assert table == []
