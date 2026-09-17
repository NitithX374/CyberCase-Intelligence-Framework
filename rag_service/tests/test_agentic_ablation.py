"""
Unit Tests for the agentic ablation benchmark
==============================================
Arm-A tracing and arm-B derivation against a scripted stand-in for the served
graph (no LLM, no databases), plus the deterministic scoring helpers.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from RAG.GraphRAG.evaluation.agentic_ablation import (
    _LlmMeter,
    _micro,
    _record_decompositions,
    derive_b,
    paired,
    run_full_agent,
    score_answer,
)
from RAG.GraphRAG.pipeline.agent_graph import GraphRAGAgent


class _Llm:
    def __init__(self, text="ok"):
        self.text = text

    def invoke(self, *_args, **_kwargs):
        return SimpleNamespace(content=self.text, usage_metadata={"input_tokens": 10, "output_tokens": 5})


class _StubAgent:
    """Enough of GraphRAGAgent for the benchmark: LLM slots, decomposer, and a
    graph whose stream() replays a scripted node sequence, calling the LLMs a
    served node would call."""

    initial_state = staticmethod(GraphRAGAgent.initial_state)
    _node_prepare = GraphRAGAgent._node_prepare
    _edge_after_reasoning = staticmethod(GraphRAGAgent._edge_after_reasoning)

    def __init__(self, script):
        self.router = SimpleNamespace(llm=_Llm())
        self.evaluator = SimpleNamespace(llm=_Llm())
        self.reasoning_llm = _Llm("branch answer T1190")
        self.translation_llm = _Llm()
        agent = self
        self.decomposer = SimpleNamespace(llm=_Llm())
        self.decomposer.decompose = lambda incident, verbose=False: [
            agent.decomposer.llm.invoke(incident) and "sub-query"
        ]
        self.script = script
        self.graph = SimpleNamespace(stream=self._stream)

    def _stream(self, state, stream_mode):
        assert stream_mode == "updates"
        for node, update in self.script:
            if node == "route_query":
                self.router.llm.invoke("q")
            elif node == "retrieve":
                self.decomposer.decompose(state["original_query"])
            elif node == "evaluate_context" and update.pop("_judged", True):
                self.evaluator.llm.invoke("q")
            elif node == "reasoning" and not update.pop("_ack", False):
                self.reasoning_llm.invoke("q")
            yield {node: update}

    def _node_reasoning(self, state):
        return {"answer": self.reasoning_llm.invoke("q").content, "answer_is_final": True}


def _evaluation(verdict, strategy="", new_query="", message=""):
    return SimpleNamespace(verdict=verdict, strategy=strategy, reason="r",
                           new_query=new_query, missing_phases=[], message=message)


def _retrieve(context):
    return {"graphrag_result": SimpleNamespace(vector_results=[1, 2], graph_results=[1]),
            "context": context}


def _run(script):
    agent = _StubAgent(script)
    meter = _LlmMeter()
    meter.attach(agent)
    log = _record_decompositions(agent)
    return agent, meter, run_full_agent(agent, meter, log, "เหตุการณ์")


def test_loop_not_fired_b_is_a():
    agent, meter, a = _run([
        ("route_query", {"route": "INCIDENT_ANALYSIS"}),
        ("prepare", {"english_query": "เหตุการณ์", "respond_in_thai": True}),
        ("retrieve", _retrieve("ctx-1")),
        ("evaluate_context", {"evaluation": _evaluation("SUFFICIENT")}),
        ("reasoning", {"answer": "A answer T1566", "answer_is_final": True}),
    ])
    assert a["llm_calls"] == 4
    assert a["calls_by_stage"] == {"router": 1, "decompose": 1, "evaluate": 1, "reasoning": 1}
    assert (a["broaden_rounds"], a["ack_limit"], a["b_identical"]) == (0, False, True)
    assert a["first_context"] == "ctx-1" and a["final_context"] is None

    calls_before = len(meter.events)
    b = derive_b(agent, meter, a, "เหตุการณ์")
    assert len(meter.events) == calls_before  # no new LLM call
    assert b["identical_to_A"] and b["answer"] == "A answer T1566"
    assert b["calls_by_stage"] == {"router": 1, "decompose": 1, "reasoning": 1}


def test_broaden_fired_b_reasons_on_first_context():
    agent, meter, a = _run([
        ("route_query", {"route": "INCIDENT_ANALYSIS"}),
        ("prepare", {"english_query": "เหตุการณ์", "respond_in_thai": True}),
        ("retrieve", _retrieve("ctx-1")),
        ("evaluate_context", {"evaluation": _evaluation("INSUFFICIENT", "BROADEN_SEARCH", "rewrite")}),
        ("broaden_search", {"rewritten_queries": ["rewrite"], "broaden_count": 1}),
        ("retrieve", _retrieve("ctx-2")),
        ("evaluate_context", {"evaluation": _evaluation("SUFFICIENT")}),
        ("reasoning", {"answer": "A answer", "answer_is_final": True}),
    ])
    assert a["calls_by_stage"] == {"router": 1, "decompose": 2, "evaluate": 2, "reasoning": 1}
    assert (a["broaden_rounds"], a["n_retrieves"], a["b_identical"]) == (1, 2, False)
    assert a["first_verdict"] == "INSUFFICIENT"
    assert (a["first_context"], a["final_context"]) == ("ctx-1", "ctx-2")

    b = derive_b(agent, meter, a, "เหตุการณ์")
    assert not b["identical_to_A"] and b["answer"] == "branch answer T1190"
    assert b["calls_by_stage"] == {"router": 1, "decompose": 1, "reasoning": 1}


def test_acknowledge_limit_detected_without_broaden():
    agent, meter, a = _run([
        ("route_query", {"route": "INCIDENT_ANALYSIS"}),
        ("prepare", {"english_query": "เหตุการณ์", "respond_in_thai": True}),
        ("retrieve", _retrieve("ctx-1")),
        ("evaluate_context", {"evaluation": _evaluation("INSUFFICIENT", "ACKNOWLEDGE_LIMIT", message="too vague")}),
        ("reasoning", {"answer": "too vague", "_ack": True}),
        ("translate_output", {"answer": "คลุมเครือ"}),
    ])
    assert (a["broaden_rounds"], a["ack_limit"], a["b_identical"]) == (0, True, False)
    b = derive_b(agent, meter, a, "เหตุการณ์")
    assert not b["identical_to_A"] and b["answer"] == "branch answer T1190"


def test_score_rolls_subtechniques_up_to_parent_gold():
    sample = {
        "gold_attack_ids": ["T1566", "T1190"],
        "attack_steps": [
            {"cue_type": "named", "gold_attack_ids": ["T1566"]},
            {"cue_type": "described", "gold_attack_ids": ["T1190"]},
        ],
    }
    s = score_answer("พบ T1566.001 และ T1566.002 กับ T1059", sample, alias_map={})
    # T1566.001/.002 collapse to one T1566 match; T1059 is spurious.
    assert (s["n_pred"], s["matched"]) == (2, 1.0)
    assert (s["precision"], s["recall"]) == (0.5, 0.5)
    assert s["f1_raw"] < s["f1"]  # without roll-up only same-family credit
    assert s["step_recall"] == {"named": [1.0], "described": [0.0]}


def test_micro_pools_and_paired_counts():
    a = {"matched": 1.0, "n_pred": 2, "n_gold": 2}
    b = {"matched": 0.0, "n_pred": 0, "n_gold": 3}
    assert _micro([a, b]) == pytest.approx((0.5, 0.2, 2 * 0.5 * 0.2 / 0.7))

    st = paired({"x": 0.5, "y": 0.2, "z": 0.1}, {"x": 0.5, "y": 0.4, "z": 0.0}, ["x", "y", "z"])
    assert (st["wins"], st["ties"], st["losses"]) == (1, 1, 1)
    assert abs(st["mean"] - (-0.1 / 3)) < 1e-9
