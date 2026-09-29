"""
Unit Tests for the reasoning node and the graph's answer path
=============================================================
One call writes the final answer in the query's language; the graph ends at
``reasoning``; an ACKNOWLEDGE_LIMIT note reaches a Thai reader in Thai.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.pipeline.agent_graph import GraphRAGAgent, _THAI_LIMIT_NOTE
from RAG.GraphRAG.pipeline.cross_lingual import CrossLingualLayer
from RAG.GraphRAG.pipeline.evaluator import VERDICT_INSUFFICIENT


class _RecordingLlm:
    def __init__(self, text="คำตอบ T1566"):
        self.text = text
        self.messages = None

    def invoke(self, messages, **_kwargs):
        self.messages = messages
        return SimpleNamespace(content=self.text)


def _agent(text="คำตอบ T1566"):
    agent = GraphRAGAgent.__new__(GraphRAGAgent)  # no models, no DB
    agent.reasoning_llm = _RecordingLlm(text)
    return agent


def _state(respond_in_thai, **extra):
    return {"verbose": False, "context": "ctx", "original_query": "q",
            "english_query": "q", "respond_in_thai": respond_in_thai, **extra}


def _ack(message, broaden_count=0):
    return {"strategy": "ACKNOWLEDGE_LIMIT", "acknowledgement_message": message,
            "evaluation": SimpleNamespace(verdict=VERDICT_INSUFFICIENT),
            "broaden_count": broaden_count}


class TestReasoningNode:
    def test_thai_query_gets_the_thai_prompt_and_a_final_answer(self):
        agent = _agent()
        out = agent._node_reasoning(_state(True))
        assert out == {"answer": "คำตอบ T1566"}
        assert agent.reasoning_llm.messages[0].content == \
            CrossLingualLayer.get_fast_system_prompt(respond_in_thai=True)

    def test_english_query_gets_the_english_prompt(self):
        agent = _agent("answer T1566")
        out = agent._node_reasoning(_state(False))
        assert out == {"answer": "answer T1566"}
        assert agent.reasoning_llm.messages[0].content == \
            CrossLingualLayer.get_reasoning_system_prompt()

    def test_thai_limit_note_is_returned_as_written(self):
        agent = _agent()
        out = agent._node_reasoning(_state(True, **_ack("คำอธิบายเหตุการณ์ยังไม่ละเอียดพอ")))
        assert out == {"answer": "คำอธิบายเหตุการณ์ยังไม่ละเอียดพอ"}
        assert agent.reasoning_llm.messages is None  # no model call on the gate

    def test_english_limit_note_on_a_thai_query_is_replaced_by_the_thai_note(self):
        out = _agent()._node_reasoning(_state(True, **_ack("The description is too vague.")))
        assert out == {"answer": _THAI_LIMIT_NOTE}

    def test_english_limit_note_on_an_english_query_is_kept(self):
        out = _agent()._node_reasoning(_state(False, **_ack("The description is too vague.")))
        assert out == {"answer": "The description is too vague."}

    def test_note_after_a_broaden_round_rides_along_in_thai(self):
        out = _agent()._node_reasoning(_state(True, **_ack("not enough data", broaden_count=1)))
        assert out == {"answer": f"คำตอบ T1566\n\n{_THAI_LIMIT_NOTE}"}


class TestGraph:
    def test_reasoning_is_the_last_node(self):
        graph = GraphRAGAgent.__new__(GraphRAGAgent)._build_graph().get_graph()
        assert "translate_output" not in graph.nodes
        assert any(e.source == "reasoning" and e.target == "__end__" for e in graph.edges)
