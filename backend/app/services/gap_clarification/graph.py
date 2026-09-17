from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.services.gap_clarification.contracts import GapClarificationState
from app.services.gap_clarification.nodes import (
    ask_user,
    commit_answer,
    evaluate_gap,
    interpret_answer,
    select_question,
)


def build_gap_clarification_graph(
    checkpointer: BaseCheckpointSaver,
):
    graph = StateGraph(GapClarificationState)
    graph.add_node("select_question", select_question)
    graph.add_node("ask_user", ask_user)
    graph.add_node("interpret_answer", interpret_answer)
    graph.add_node("commit_answer", commit_answer)
    graph.add_node("evaluate_gap", evaluate_gap)
    graph.add_edge(START, "select_question")
    graph.add_conditional_edges(
        "select_question",
        route_question_decision,
        {"ask": "ask_user", "complete": END},
    )
    graph.add_edge("ask_user", "interpret_answer")
    graph.add_edge("interpret_answer", "commit_answer")
    graph.add_edge("commit_answer", "evaluate_gap")
    graph.add_conditional_edges(
        "evaluate_gap",
        route_gap_resolution,
        {"continue": "select_question", "complete": END},
    )
    return graph.compile(checkpointer=checkpointer)


def route_question_decision(state: GapClarificationState) -> str:
    return "ask" if state.get("pending_question_message_id") else "complete"


def route_gap_resolution(state: GapClarificationState) -> str:
    return "continue" if state.get("resolution_status") == "unresolved" else "complete"


__all__ = ["build_gap_clarification_graph"]
