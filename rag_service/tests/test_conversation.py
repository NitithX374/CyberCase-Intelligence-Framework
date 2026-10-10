"""The case conversation: what a turn does, and what it must never do."""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage
from RAG.GraphRAG.pipeline.conversation import (
    ANALYSIS,
    ANSWER,
    CASE,
    FACTS,
    Analysis,
    CaseChat,
    Conversation,
    ConversationBusy,
    ConversationStore,
    case_with_facts,
)
from RAG.GraphRAG.pipeline.conversation.case_chat import named_ids, parse_plan
from RAG.GraphRAG.pipeline.conversation.prompts import history_text
from RAG.GraphRAG.pipeline.mitre_table import EvidenceSpan, MitreTableRow
from RAG.GraphRAG.retrieval.graph_retriever import GraphEdge, GraphNode, SubgraphResult
from RAG.GraphRAG.retrieval.hybrid_retriever import GraphRAGResult
from RAG.GraphRAG.retrieval.vector_retriever import VectorResult

CASE_FILE = "คนร้ายส่งคำสั่งฐานข้อมูลแทรกเข้าทางหน้าเว็บ แล้วดาวน์โหลดสคริปต์เข้ามาไว้บนเครื่อง"
SENTENCE = "คนร้ายส่งคำสั่งฐานข้อมูลแทรกเข้าทางหน้าเว็บ"


def row(attack_id: str, name: str, sentence: str = "") -> MitreTableRow:
    evidence = None
    if sentence:
        start = CASE_FILE.index(sentence)
        evidence = [EvidenceSpan(text=sentence, start=start, end=start + len(sentence), basis="reread")]
    return MitreTableRow(
        technique_id=attack_id, name=name, entity_type="Technique", tactic="Initial Access",
        description=f"Definition of {name}.", evidence=evidence,
    )


class FakeLlm:
    """Replies in order; an exception in the list is raised instead."""

    def __init__(self, *replies) -> None:
        self.replies = list(replies)
        self.prompts: list[tuple[str, str]] = []

    def invoke(self, messages):
        self.prompts.append((messages[0].content, messages[1].content))
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return AIMessage(content=reply)


# T1105 is Enterprise. T1513 is the Mobile matrix's Screen Capture, which
# shares its name with Enterprise T1113.
NAMES = {"T1105": "Ingress Tool Transfer", "T1513": "Screen Capture"}
MOBILE = {"attack-pattern--T1513", "course-of-action--mobile"}


def subgraph(attack_id: str) -> SubgraphResult:
    name = NAMES[attack_id]
    return SubgraphResult(
        center_node=GraphNode(stix_id=f"attack-pattern--{attack_id}", name=name,
                              label="Technique", attack_id=attack_id),
        neighbors=[
            GraphNode(stix_id="course-of-action--1", name="Network Intrusion Prevention", label="Mitigation"),
            GraphNode(stix_id="intrusion-set--1", name="Sandworm Team", label="Group"),
            GraphNode(stix_id="tool--1", name="sqlmap", label="Software"),
        ],
        edges=[
            GraphEdge("MITIGATES", "Network Intrusion Prevention", name),
            GraphEdge("USES", "Sandworm Team", name),
            GraphEdge("USES", "sqlmap", name),
        ],
    )


class FakeGraph:
    def __init__(self, fail: bool = False) -> None:
        self.asked: list[list[str]] = []
        self.fail = fail

    def stix_ids_for(self, attack_ids):
        self.asked.append(list(attack_ids))
        if self.fail:
            raise RuntimeError("neo4j is down")
        return {aid: f"attack-pattern--{aid}" for aid in attack_ids if aid in NAMES}

    def entity_details(self, stix_ids):
        return {sid: {"description": "Adversaries may transfer tools from an external system.",
                      "tactics": ["Command and Control"]} for sid in stix_ids}

    def domains_of(self, stix_ids):
        if self.fail:
            raise RuntimeError("neo4j is down")
        return {sid: "mobile" if sid in MOBILE else "enterprise" for sid in stix_ids}

    def expand_batch(self, stix_ids):
        return [subgraph(sid.removeprefix("attack-pattern--")) for sid in stix_ids]


class FakeRetriever:
    def __init__(self, fail: bool = False, empty: bool = False, graph: FakeGraph | None = None) -> None:
        self.searches: list[tuple[list[str], dict]] = []
        self.fail, self.empty = fail, empty
        self.graph_retriever = graph or FakeGraph()

    def retrieve_multi_quota(self, queries, **kwargs):
        self.searches.append((list(queries), kwargs))
        if self.fail:
            raise RuntimeError("qdrant is down")
        if self.empty:
            return GraphRAGResult(vector_results=[], graph_results=[])
        relationship = {"entity_type": "Relationship", "edge_label": "MITIGATES"}
        hits = [
            VectorResult(  # a Mobile mitigation of the Mobile twin: both ends outside Enterprise
                document="Application Developer Guidance: use FLAG_SECURE on Android.",
                metadata={**relationship, "source_name": "Application Developer Guidance",
                          "source_id": "course-of-action--mobile", "target_id": "attack-pattern--T1513"},
                score=0.97, stix_id="relationship--mobile",
            ),
            VectorResult(
                document="Network Intrusion Prevention blocks malicious downloads.",
                metadata={"entity_type": "Entity", "node_label": "Mitigation",
                          "name": "Network Intrusion Prevention", "attack_id": "M1031"},
                score=0.91, stix_id="course-of-action--1",
            ),
            VectorResult(
                document="Network Intrusion Prevention mitigates Ingress Tool Transfer.",
                metadata={**relationship, "source_name": "Network Intrusion Prevention",
                          "source_id": "course-of-action--1", "target_id": "attack-pattern--T1105"},
                score=0.80, stix_id="relationship--enterprise",
            ),
        ]
        return GraphRAGResult(vector_results=hits, graph_results=[subgraph("T1513"), subgraph("T1105")])


class Pipeline:
    """Stands in for the served pipeline: one analysis per call, in order."""

    def __init__(self, *tables) -> None:
        self.tables = list(tables)
        self.read: list[str] = []

    def __call__(self, case_text: str) -> Analysis:
        self.read.append(case_text)
        table = self.tables.pop(0)
        if isinstance(table, Exception):
            raise table
        return Analysis(case_text=case_text, answer=f"## สรุปเหตุการณ์ ฉบับที่ {len(self.read)}",
                        context="RETRIEVED CONTEXT: T1190 …", mitre_table=table)


def chat_with(pipeline, *, answers=(), plans=(), retriever=None):
    answer_llm, plan_llm = FakeLlm(*answers), FakeLlm(*plans)
    chat = CaseChat(answer_llm=answer_llm, plan_llm=plan_llm,
                    retriever=retriever or FakeRetriever(), analyse=pipeline)
    return chat, answer_llm, plan_llm


FIRST_TABLE = [row("T1190", "Exploit Public-Facing Application", SENTENCE)]


def test_opening_analyses_the_case_file_once_and_records_both_turns() -> None:
    pipeline = Pipeline(FIRST_TABLE)
    chat, answer_llm, plan_llm = chat_with(pipeline)

    conversation = chat.open(CASE_FILE)

    assert pipeline.read == [CASE_FILE]
    assert [(t.role, t.kind) for t in conversation.turns] == [("user", CASE), ("assistant", ANALYSIS)]
    assert conversation.turns[1].text == conversation.analysis.answer
    # Opening is the pipeline and nothing else: no call of the chat's own.
    assert answer_llm.prompts == [] and plan_llm.prompts == []


def test_question_about_the_case_runs_neither_a_search_nor_the_pipeline() -> None:
    pipeline = Pipeline(FIRST_TABLE)
    retriever = FakeRetriever()
    chat, answer_llm, _ = chat_with(pipeline, plans=["LOOKUP: no"], answers=["เพราะสำนวนระบุว่า…"],
                                    retriever=retriever)
    conversation = chat.open(CASE_FILE)

    reply = chat.say(conversation, "ทำไมถึงเป็นเทคนิคนี้")

    assert (reply.kind, reply.text) == (ANSWER, "เพราะสำนวนระบุว่า…")
    assert reply.lookup_queries == [] and reply.lookup_ids == []
    assert retriever.searches == [] and retriever.graph_retriever.asked == []
    assert pipeline.read == [CASE_FILE]
    assert conversation.analysis.mitre_table == FIRST_TABLE

    _, prompt = answer_llm.prompts[0]
    assert CASE_FILE in prompt
    assert conversation.analysis.answer in prompt
    assert "T1190 Exploit Public-Facing Application" in prompt
    assert f'case file: "{SENTENCE}"' in prompt
    assert "Definition of Exploit Public-Facing Application." in prompt
    assert "looked up for this message" not in prompt
    assert prompt.rstrip().endswith("ทำไมถึงเป็นเทคนิคนี้")


def test_question_needing_attack_knowledge_searches_every_entity_type() -> None:
    retriever = FakeRetriever()
    plan = "LOOKUP: yes\nQUERY: **วิธีป้องกัน** การนำไฟล์เข้ามา (Ingress Tool Transfer mitigation) T1105\nQUERY: second"
    chat, answer_llm, _ = chat_with(Pipeline(FIRST_TABLE), plans=[plan], answers=["ป้องกันได้โดย…"],
                                    retriever=retriever)
    conversation = chat.open(CASE_FILE)

    reply = chat.say(conversation, "ป้องกันยังไง")

    queries, kwargs = retriever.searches[0]
    # Markdown and the bare ID are stripped before the query is embedded.
    assert queries == ["วิธีป้องกัน การนำไฟล์เข้ามา (Ingress Tool Transfer mitigation)", "second"]
    # A mitigation is not in the technique pool the case analysis retrieves from.
    assert kwargs["technique_pool"] is False
    assert reply.lookup_queries == queries
    _, prompt = answer_llm.prompts[0]
    looked_up = prompt.split("looked up for this message")[1].split("CONVERSATION SO FAR")[0]
    assert "Network Intrusion Prevention (M1031)" in looked_up
    assert "Network Intrusion Prevention mitigates Ingress Tool Transfer." in looked_up
    assert "## Technique: Ingress Tool Transfer (T1105)" in looked_up


def test_a_search_keeps_what_another_attack_domain_says_out_of_the_answer() -> None:
    """Relationship documents carry no domain. With the technique pool off, the
    Mobile matrix's guidance for Screen Capture reached a question about the
    Enterprise technique of the same name."""
    retriever = FakeRetriever()
    chat, answer_llm, _ = chat_with(Pipeline(FIRST_TABLE), plans=["LOOKUP: yes\nQUERY: screen capture mitigation"],
                                    answers=["…"], retriever=retriever)
    conversation = chat.open(CASE_FILE)

    chat.say(conversation, "ป้องกันการบันทึกภาพหน้าจอยังไง")

    _, kwargs = retriever.searches[0]
    assert kwargs["per_query_k"] == 6  # twice the quota, so that dropping leaves enough
    _, prompt = answer_llm.prompts[0]
    assert "FLAG_SECURE" not in prompt and "Application Developer Guidance" not in prompt
    assert "(T1513)" not in prompt


def test_an_id_the_reader_names_is_read_from_the_graph_not_searched_for() -> None:
    retriever = FakeRetriever()
    chat, answer_llm, plan_llm = chat_with(Pipeline(FIRST_TABLE), plans=["LOOKUP: no"],
                                           answers=["T1105 คือ…"], retriever=retriever)
    conversation = chat.open(CASE_FILE)

    reply = chat.say(conversation, "t1105 กับ T9999 คืออะไร")

    assert retriever.graph_retriever.asked == [["T1105", "T9999"]]
    assert retriever.searches == []
    assert reply.lookup_ids == ["T1105"]  # T9999 is not in the graph, so nothing rests on it
    _, prompt = answer_llm.prompts[0]
    assert "## Technique: Ingress Tool Transfer (T1105)\n" in prompt  # Enterprise: no label
    assert "Adversaries may transfer tools from an external system." in prompt
    # Each neighbour under its own kind: one "Used by" list had a live answer
    # name malware and tools as groups.
    assert "Mitigated by — Mitigation: Network Intrusion Prevention" in prompt
    assert "Used by — Group: Sandworm Team\n" in prompt
    assert "Used by — Software: sqlmap" in prompt
    # The planning call is told, so it does not search for what is in hand.
    _, plan = plan_llm.prompts[0]
    assert "\nT1105\n" in plan.split("ALREADY FETCHED")[1].split("CONVERSATION SO FAR")[0]


def test_a_named_id_from_another_matrix_is_shown_and_labelled() -> None:
    chat, answer_llm, _ = chat_with(Pipeline(FIRST_TABLE), plans=["LOOKUP: no"], answers=["…"])
    conversation = chat.open(CASE_FILE)

    reply = chat.say(conversation, "T1513 คืออะไร")

    assert reply.lookup_ids == ["T1513"]
    _, prompt = answer_llm.prompts[0]
    assert "## Technique: Screen Capture (T1513) — MOBILE ATT&CK, not Enterprise" in prompt


def test_a_failed_plan_or_lookup_costs_the_lookup_not_the_answer() -> None:
    retriever = FakeRetriever(fail=True, graph=FakeGraph(fail=True))
    chat, answer_llm, _ = chat_with(
        Pipeline(FIRST_TABLE, FIRST_TABLE),
        plans=[RuntimeError("provider timeout"), "LOOKUP: yes\nQUERY: mitigation"],
        answers=["ตอบจากสำนวน", "ตอบจากสำนวนอีกครั้ง"],
        retriever=retriever,
    )
    conversation = chat.open(CASE_FILE)

    first = chat.say(conversation, "T1105 คืออะไร")   # planning fails, the graph fails
    second = chat.say(conversation, "ป้องกันยังไง")    # the search fails

    assert (first.text, second.text) == ("ตอบจากสำนวน", "ตอบจากสำนวนอีกครั้ง")
    for reply in (first, second):
        assert reply.lookup_queries == [] and reply.lookup_ids == []
    assert all("looked up for this message" not in prompt for _, prompt in answer_llm.prompts)


def test_a_search_that_finds_nothing_is_not_reported_as_a_source() -> None:
    chat, _, _ = chat_with(Pipeline(FIRST_TABLE), plans=["LOOKUP: yes\nQUERY: something"],
                           answers=["ฐานความรู้ไม่มีข้อมูลเรื่องนี้"], retriever=FakeRetriever(empty=True))
    conversation = chat.open(CASE_FILE)

    assert chat.say(conversation, "เรื่องอื่น").lookup_queries == []


def test_added_facts_analyse_the_whole_case_again_and_say_what_changed() -> None:
    second_table = [row("T1190", "Exploit Public-Facing Application", SENTENCE),
                    row("T1486", "Data Encrypted for Impact")]
    pipeline = Pipeline([*FIRST_TABLE, row("T1105", "Ingress Tool Transfer")], second_table)
    chat, answer_llm, plan_llm = chat_with(pipeline)
    conversation = chat.open(CASE_FILE)

    reply = chat.say(conversation, "ไฟล์งานถูกเข้ารหัสลับทั้งหมด", kind=FACTS)

    assert pipeline.read[1] == f"{CASE_FILE}\n\nข้อเท็จจริงเพิ่มเติม:\n- ไฟล์งานถูกเข้ารหัสลับทั้งหมด"
    assert conversation.analysis.case_text == pipeline.read[1]
    assert conversation.analysis.mitre_table == second_table
    assert (reply.kind, reply.rows_added, reply.rows_removed) == (ANALYSIS, ["T1486"], ["T1105"])
    assert [t.kind for t in conversation.turns] == [CASE, ANALYSIS, FACTS, ANALYSIS]
    # Facts go to the pipeline; the chat's own two calls are not involved.
    assert answer_llm.prompts == [] and plan_llm.prompts == []

    # A second batch is appended to the first, not swapped for it.
    pipeline.tables.append(second_table)
    chat.say(conversation, "มีข้อความเรียกค่าไถ่", kind=FACTS)
    assert pipeline.read[2].endswith("- ไฟล์งานถูกเข้ารหัสลับทั้งหมด\n- มีข้อความเรียกค่าไถ่")


def test_a_reanalysis_that_fails_leaves_the_conversation_as_it_was() -> None:
    chat, _, _ = chat_with(Pipeline(FIRST_TABLE, RuntimeError("model unavailable")))
    conversation = chat.open(CASE_FILE)
    analysis = conversation.analysis

    with pytest.raises(RuntimeError):
        chat.say(conversation, "ข้อเท็จจริงใหม่", kind=FACTS)

    assert conversation.analysis is analysis
    assert conversation.facts == [] and len(conversation.turns) == 2
    assert not conversation.busy.locked()


def test_a_conversation_answers_one_message_at_a_time() -> None:
    chat, _, _ = chat_with(Pipeline(FIRST_TABLE))
    conversation = chat.open(CASE_FILE)

    with conversation.busy, pytest.raises(ConversationBusy):
        chat.say(conversation, "คำถาม")


def test_history_carries_the_dialogue_and_leaves_the_documents_out() -> None:
    pipeline = Pipeline(FIRST_TABLE, FIRST_TABLE)
    chat, answer_llm, _ = chat_with(pipeline, plans=["LOOKUP: no", "LOOKUP: no"],
                                    answers=["คำตอบแรก " + "ยาว" * 2000, "คำตอบที่สอง"])
    conversation = chat.open(CASE_FILE)
    chat.say(conversation, "คำถามแรก")
    chat.say(conversation, "ข้อเท็จจริงใหม่", kind=FACTS)
    chat.say(conversation, "คำถามที่สอง")

    history = history_text(conversation.turns[:-2])  # as the last question saw it

    assert CASE_FILE not in history and "สรุปเหตุการณ์" not in history
    assert history.splitlines() == [
        "Reader: คำถามแรก",
        history.splitlines()[1],
        "Reader (added facts): ข้อเท็จจริงใหม่",
        "Assistant: [analysed the case again — the current analysis is above]",
    ]
    assert history.splitlines()[1].startswith("Assistant: คำตอบแรก") and history.splitlines()[1].endswith("…")
    assert len(history.splitlines()[1]) < 1600
    # And that is what the model was shown, under the current analysis.
    _, prompt = answer_llm.prompts[1]
    assert history in prompt and "ฉบับที่ 2" in prompt and "ฉบับที่ 1" not in prompt


@pytest.mark.parametrize(
    ("reply", "expected"),
    [
        ("LOOKUP: no", []),
        ("", []),
        ("I think a lookup would help.", []),
        ("lookup: YES\nquery: one\nQUERY: one\nQUERY: two", ["one", "two"]),
        ("LOOKUP: yes\nQUERY: a\nQUERY: b\nQUERY: c\nQUERY: d", ["a", "b", "c"]),
        ("LOOKUP: yes", ["what is lateral movement"]),       # yes without a query → the message
        ("LOOKUP: yes\nQUERY: T1105", ["what is lateral movement"]),  # nothing left after cleaning
        # As a live reply had it: the ID is taken out, and so is the gap it leaves.
        ("LOOKUP: yes\nQUERY: คืออะไร (T1486 Data Encrypted for Impact)", ["คืออะไร (Data Encrypted for Impact)"]),
    ],
)
def test_plan_replies(reply: str, expected: list[str]) -> None:
    assert parse_plan(reply, "what is lateral movement") == expected


def test_named_ids_are_read_in_any_case_once_each_and_capped() -> None:
    assert named_ids("t1105 กับ T1105 และ ta0011, g0016") == ["T1105", "TA0011", "G0016"]
    assert named_ids("T1001 T1002 T1003 T1004 T1005") == ["T1001", "T1002", "T1003", "T1004"]
    assert named_ids("ไม่มีรหัส AT1105X CVE-2024-12345") == []
    # Thai runs straight into the ID, and its letters are word characters.
    assert named_ids("อธิบายT1059.001หน่อย") == ["T1059.001"]


def test_added_facts_are_headed_in_the_language_of_the_case() -> None:
    assert case_with_facts("สำนวน", []) == "สำนวน"
    assert case_with_facts("สำนวน\n", [" ก ", "ข"]) == "สำนวน\n\nข้อเท็จจริงเพิ่มเติม:\n- ก\n- ข"
    assert case_with_facts("The case", ["a"]) == "The case\n\nAdditional facts:\n- a"


# ── the store ────────────────────────────────────────────────────────────────
class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def conversation() -> Conversation:
    return Conversation(case_file="x", analysis=Analysis(case_text="x", answer="", context=""))


def test_store_forgets_a_conversation_left_idle_but_not_one_in_use() -> None:
    clock = Clock()
    store = ConversationStore(ttl_seconds=60, capacity=10, clock=clock)
    idle, used, answering = conversation(), conversation(), conversation()
    for c in (idle, used, answering):
        store.add(c)

    clock.now += 50
    assert store.get(used.id) is used          # counts as use
    clock.now += 20                             # idle and answering are now 70 s old
    with answering.busy:
        assert store.get(idle.id) is None
        assert store.get(used.id) is used
        assert store.get(answering.id) is answering   # mid-message, so kept


def test_store_past_capacity_drops_the_least_recently_used() -> None:
    clock = Clock()
    store = ConversationStore(ttl_seconds=3600, capacity=2, clock=clock)
    first, second, third = conversation(), conversation(), conversation()
    store.add(first)
    clock.now += 1
    store.add(second)
    clock.now += 1
    store.get(first.id)                          # first is now the fresher of the two
    clock.now += 1
    store.add(third)

    assert len(store) == 2
    assert store.get(second.id) is None
    assert store.get(first.id) is first and store.get(third.id) is third


def test_store_delete() -> None:
    store = ConversationStore()
    c = conversation()
    store.add(c)

    assert store.delete(c.id) is True
    assert store.delete(c.id) is False
    assert store.get(c.id) is None
