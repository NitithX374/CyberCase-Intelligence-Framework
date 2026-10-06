"""
Unit Tests for case evidence
============================
A table row is traced to the part of the case file it rests on. A sentence a
model copied is looked up in the case file and only the place it is found at
leaves the service. The re-read keeps the sentence behind each technique,
retrieval keeps which sub-queries returned an entity, a sub-query is found in
the case file by its own words, and a row lists the re-read's evidence, with
retrieval's only when the re-read has none.
"""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.pipeline.case_evidence import (
    CaseEvidence,
    locate,
    locate_query,
    merge_spans,
    provenance_key,
)
from RAG.GraphRAG.pipeline.mitre_table import MitreTableRow, build_mitre_table
from RAG.GraphRAG.pipeline.table_reread import (
    SHORTLIST_SYSTEM,
    SHORTLIST_WITH_SENTENCES_SYSTEM,
    TableReread,
    TechniqueSelection,
    build_catalogue,
    reply_ids,
    reply_steps,
)
from RAG.GraphRAG.retrieval.hybrid_retriever import GraphRAGResult, HybridRetriever, merge_results
from RAG.GraphRAG.retrieval.vector_retriever import VectorResult
from routers import rag as rag_router

CASE = (
    "เมื่อวันที่ 3 มีนาคม 2567 ผู้เสียหายได้รับอีเมลแนบไฟล์ Excel ที่ฝัง macro "
    "เมื่อเปิดไฟล์ เครื่องเชื่อมต่อออกไปยังเซิร์ฟเวอร์ของคนร้าย "
    "ต่อมาคนร้ายเข้ารหัสไฟล์ทั้งหมดบนเครื่องแม่ข่ายเพื่อเรียกค่าไถ่"
)
MAIL = "ผู้เสียหายได้รับอีเมลแนบไฟล์ Excel ที่ฝัง macro"
ENCRYPT = "คนร้ายเข้ารหัสไฟล์ทั้งหมดบนเครื่องแม่ข่ายเพื่อเรียกค่าไถ่"
# Sub-queries as the decomposer writes them: the incident's words, then a gloss.
MAIL_QUERY = "ได้รับอีเมลแนบไฟล์ Excel ที่ฝัง macro (spearphishing attachment)"
RANSOM_QUERY = "เข้ารหัสไฟล์ทั้งหมดบนเครื่องแม่ข่าย (data encrypted for impact)"
MAIL_WORDS = "ได้รับอีเมลแนบไฟล์ Excel ที่ฝัง macro"
RANSOM_WORDS = "เข้ารหัสไฟล์ทั้งหมดบนเครื่องแม่ข่าย"


def span_of(text):
    at = CASE.index(text)
    return at, at + len(text)


# ── finding a copied sentence ─────────────────────────────────────────────────


def test_a_sentence_copied_exactly_is_found_where_it_is():
    assert locate(ENCRYPT, CASE) == span_of(ENCRYPT)


def test_spacing_and_quotation_marks_do_not_stop_a_copy_being_found():
    respaced = "“ผู้เสียหายได้รับอีเมล แนบไฟล์ Excel ที่ฝัง  macro…”"

    assert locate(respaced, CASE) == span_of(MAIL)


def test_a_copy_with_a_few_words_dropped_is_still_found():
    start, end = locate("คนร้ายเข้ารหัสไฟล์บนเครื่องแม่ข่ายเพื่อเรียกค่าไถ่", CASE)

    # What comes back is the case file's own text, not the model's version.
    assert CASE[start:end] == ENCRYPT


def test_what_the_case_file_does_not_say_is_not_found():
    assert locate("คนร้ายลบฐานข้อมูลลูกค้าทั้งหมดแล้วหลบหนี", CASE) is None
    assert locate("macro", CASE) is None  # too short to be a sentence
    assert locate("", CASE) is None
    assert locate(MAIL, "") is None


def test_overlapping_spans_are_joined_and_put_in_order():
    assert merge_spans([(30, 40), (5, 10), (8, 20), (5, 10)]) == [(5, 20), (30, 40)]


def test_a_technique_is_filed_under_its_parent_and_anything_else_under_its_own_id():
    assert provenance_key("T1566.001", "attack-pattern--x") == "T1566"
    assert provenance_key("t1486", "attack-pattern--y") == "T1486"
    assert provenance_key("S0002", "tool--mimikatz") == "tool--mimikatz"
    assert provenance_key("", "") == ""


# ── finding a sub-query ───────────────────────────────────────────────────────


def test_a_sub_query_is_found_by_its_own_words_without_its_gloss():
    assert locate_query(MAIL_QUERY, CASE) == span_of(MAIL_WORDS)
    assert locate_query(RANSOM_WORDS, CASE) == span_of(RANSOM_WORDS)


def test_the_whole_incident_and_a_rewrite_in_other_words_point_at_nothing():
    # The holistic channel sends the case file itself as one query.
    assert locate_query(CASE, CASE) is None
    # A broaden round's rewrite is written in ATT&CK's words, not the case file's.
    assert locate_query("phishing email with a malicious attachment", CASE) is None
    assert locate_query("ยกระดับสิทธิ์เป็นผู้ดูแลระบบ (privilege escalation)", CASE) is None


# ── retrieval keeps which sub-queries returned an entity ──────────────────────


def hit(sid, name, label, attack_id, score=0.9):
    md = {"entity_type": "Node", "node_label": label, "name": name, "attack_id": attack_id}
    return VectorResult(document=f"{label}: {name}. About {name}.", metadata=md, score=score, stix_id=sid)


def test_every_sub_query_that_returned_a_technique_is_recorded():
    retriever = HybridRetriever.__new__(HybridRetriever)  # no models, no DB
    retriever._attack_ids = {}
    answers = {
        "whole": [hit("p", "Phishing", "Technique", "T1566"), hit("e", "Data Encrypted", "Technique", "T1486")],
        "mail": [hit("pa", "Spearphishing Attachment", "Subtechnique", "T1566.001"), hit("m", "Mimikatz", "Software", "S0002")],
        "ransom": [hit("e", "Data Encrypted", "Technique", "T1486")],
    }
    retriever.retrieve = lambda query, **_: GraphRAGResult(vector_results=answers[query], graph_results=[])

    result = retriever.retrieve_multi_quota(["whole", "mail", "ransom"], per_query_k=2, technique_pool=True)

    # T1566 keeps both queries although the merged list holds one hit for it.
    assert result.retrieved_by == {
        "T1566": ["whole", "mail"],
        "T1486": ["whole", "ransom"],
        "m": ["mail"],
    }
    kept = [vr.stix_id for vr in result.vector_results]
    assert kept.count("p") + kept.count("pa") == 1


def test_a_broaden_round_adds_its_queries_to_the_ones_already_recorded():
    first = GraphRAGResult(vector_results=[], graph_results=[], retrieved_by={"T1566": ["mail"]})
    second = GraphRAGResult(
        vector_results=[], graph_results=[], retrieved_by={"T1566": ["mail", "rewrite"], "T1486": ["rewrite"]}
    )

    assert merge_results(first, second).retrieved_by == {"T1566": ["mail", "rewrite"], "T1486": ["rewrite"]}
    assert first.retrieved_by == {"T1566": ["mail"]}  # the earlier round is not edited


# ── the re-read keeps the sentence behind each technique ──────────────────────


def catalogue_row(attack_id, name):
    return {
        "stix_id": f"attack-pattern--{attack_id}",
        "attack_id": attack_id,
        "name": name,
        "description": f"Adversaries may use {name}.",
        "tactics": [{"shortname": "impact", "name": "Impact"}],
        "sub_names": [],
    }


ROWS = [catalogue_row("T1566", "Phishing"), catalogue_row("T1486", "Data Encrypted for Impact")]


def steps(*pairs):
    return json.dumps(
        {"steps": [{"step": "ขั้นตอน", "sentence": sentence, "technique_id": tid} for tid, sentence in pairs]},
        ensure_ascii=False,
    )


def test_the_shortlist_prompt_asks_for_the_sentence_and_a_reply_is_read_with_it():
    assert '"sentence"' in SHORTLIST_WITH_SENTENCES_SYSTEM
    assert "word for word" in SHORTLIST_WITH_SENTENCES_SYSTEM
    assert '"sentence"' not in SHORTLIST_SYSTEM and "word for word" not in SHORTLIST_SYSTEM
    assert "{" + '"steps": [{"step"' in SHORTLIST_SYSTEM  # the braces are the JSON's, not a template's

    raw = steps(("T1566.001", MAIL), ("NONE", "x"), ("T1486", ENCRYPT), ("T1566", "ซ้ำ"))

    assert reply_steps(raw, {"T1566", "T1486"}) == [("T1566", MAIL), ("T1486", ENCRYPT)]
    assert reply_ids(raw, {"T1566", "T1486"}) == ["T1566", "T1486"]
    # A reply without the field still votes; it has no sentence.
    assert reply_steps('{"steps": [{"technique_id": "T1566"}]}', {"T1566"}) == [("T1566", "")]


def reread_with(shortlist_replies, systems=None, **kwargs):
    replies = {True: [steps(("T1566", ""), ("T1486", ""))] * 3, False: list(shortlist_replies)}

    def invoke(messages):
        full_list = "TECHNIQUES\n" in messages[1].content
        if systems is not None and not full_list:
            systems.append(messages[0].content)
        reply = replies[full_list].pop(0)
        return SimpleNamespace(text=reply, content=reply)

    return TableReread(SimpleNamespace(invoke=invoke), lambda: ROWS, readings=3, votes=2, **kwargs)


def test_sentences_are_asked_for_only_when_rows_carry_evidence():
    asked = []
    reread_with([steps(("T1566", MAIL))] * 3, asked, copy_sentences=True).select(CASE, "")
    assert set(asked) == {SHORTLIST_WITH_SENTENCES_SYSTEM}

    asked = []
    reread_with([steps(("T1566", MAIL))] * 3, asked, copy_sentences=False).select(CASE, "")
    assert set(asked) == {SHORTLIST_SYSTEM}


def test_a_kept_techniques_spans_are_where_its_sentences_are_in_the_case_file():
    reread = reread_with(
        [
            steps(("T1566", MAIL), ("T1486", ENCRYPT)),
            # Reworded past finding for T1566; the tail only for T1486.
            steps(("T1566", "ผู้เสียหายถูกหลอกให้โอนเงินผ่านแอปธนาคาร"), ("T1486", "เข้ารหัสไฟล์ทั้งหมดบนเครื่องแม่ข่ายเพื่อเรียกค่าไถ่")),
            steps(("T1566", MAIL)),
        ]
    )
    trace = {}

    selection = reread.select(CASE, "", trace)

    assert selection.spans == {"T1566": (span_of(MAIL),), "T1486": (span_of(ENCRYPT),)}
    assert trace["spans"] == {"T1566": [list(span_of(MAIL))], "T1486": [list(span_of(ENCRYPT))]}
    assert len(trace["quotes"]["T1566"]) == 3  # what was copied, found or not


def test_a_technique_whose_sentences_cannot_be_found_is_kept_without_spans():
    reread = reread_with([steps(("T1566", "ข้อความที่ไม่มีอยู่ในสำนวนเลยแม้แต่น้อย"))] * 3)

    selection = reread.select(CASE, "")

    assert [e.attack_id for e in selection.kept] == ["T1566"]
    assert selection.spans == {"T1566": ()}


# ── the row ───────────────────────────────────────────────────────────────────


def selection_with(spans):
    catalogue = build_catalogue(ROWS)
    return TechniqueSelection(
        kept=tuple(e for e in catalogue if e.attack_id in spans),
        considered=frozenset(e.attack_id for e in catalogue),
        spans=spans,
    )


def result_with(retrieved_by):
    return GraphRAGResult(
        vector_results=[
            hit("attack-pattern--T1566", "Phishing", "Technique", "T1566"),
            hit("pa", "Spearphishing Attachment", "Subtechnique", "T1566.001"),
            hit("tool--mimikatz", "Mimikatz", "Software", "S0002"),
        ],
        graph_results=[],
        retrieved_by=retrieved_by,
    )


def test_a_row_lists_the_rereads_evidence_and_retrievals_only_without_it():
    # T1566 was also returned by the sub-query about the ransom, which is the
    # wrong sentence for it, and by the whole incident, which is no sentence.
    result = result_with({"T1566": [RANSOM_QUERY, CASE], "tool--mimikatz": [RANSOM_QUERY]})
    selection = selection_with({"T1566": (span_of(MAIL),), "T1486": ()})
    evidence = CaseEvidence.build(CASE, selection=selection, rag_result=result)

    rows = {
        r.technique_id: r
        for r in build_mitre_table(
            result, "คำตอบอ้าง T1566.001 และ S0002", selection=selection, evidence=evidence
        )
    }

    start, end = span_of(MAIL)
    assert [(s.start, s.end, s.text, s.basis) for s in rows["T1566"].evidence] == [(start, end, MAIL, "reread")]
    # A sub-technique rests on what its parent rests on.
    assert rows["T1566.001"].evidence == rows["T1566"].evidence
    # Software is never re-read; where the sub-query that found it is, is all there is.
    assert [(s.text, s.basis) for s in rows["S0002"].evidence] == [(RANSOM_WORDS, "retrieval")]
    # Kept by the re-read, never retrieved, and its sentence was not found.
    assert rows["T1486"].evidence == []
    for row in rows.values():
        assert all(CASE[s.start : s.end] == s.text for s in row.evidence)


def test_retrieval_alone_can_tie_a_technique_to_a_place_in_the_case_file():
    result = result_with({"T1566": [MAIL_QUERY, "phishing email with a malicious attachment"]})
    evidence = CaseEvidence.build(CASE, rag_result=result)

    rows = build_mitre_table(result, "คำตอบอ้าง T1566", evidence=evidence)

    assert [(s.text, s.basis) for s in rows[0].evidence] == [(MAIL_WORDS, "retrieval")]


def test_a_table_built_without_evidence_has_rows_exactly_as_before():
    row = build_mitre_table(result_with({}), "คำตอบอ้าง T1566")[0]

    assert row.evidence is None
    assert "evidence" not in row.model_dump()
    assert "evidence" not in json.loads(row.model_dump_json())
    assert MitreTableRow(name="x", evidence=[]).model_dump()["evidence"] == []


def agent():
    result = result_with({"T1566": [MAIL_QUERY]})
    return SimpleNamespace(
        query=lambda query, verbose: SimpleNamespace(
            answer="คำตอบอ้าง T1566", context="ctx", graphrag_result=result
        )
    )


def test_the_route_sends_evidence_unless_it_is_switched_off(monkeypatch):
    _, table = rag_router._run_pipeline(agent(), CASE)
    assert [(s.text, s.basis) for s in table[0].evidence] == [(MAIL_WORDS, "retrieval")]

    monkeypatch.setattr(rag_router, "MITRE_TABLE_EVIDENCE", False)
    _, table = rag_router._run_pipeline(agent(), CASE)
    assert table[0].evidence is None
