import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from app.nodes.budget import budget_calculator
from app.nodes.feedback_router import feedback_router
from app.nodes.human_approval import human_approval
from app.nodes.llm_evaluator import llm_evaluator
from app.nodes.planner import planner
from app.nodes.researchers import (
    accommodation_researcher,
    activities_researcher,
    transport_researcher,
)
from app.nodes.review_steps import finalize, reviser
from app.nodes.rule_checks import rule_checks
from app.nodes.synthesizer import synthesizer
from app.state import TravelState


MAX_REVISIONS = 2
MAX_HUMAN_ROUNDS = 3
CHECKPOINT_DB = "checkpoints.sqlite"

RESEARCHERS = [
    "transport_researcher",
    "accommodation_researcher",
    "activities_researcher",
]

RERUN_NODES = {
    "transport": "rerun_transport",
    "accommodation": "rerun_accommodation",
    "activities": "rerun_activities",
}


def route_after_rules(state: TravelState) -> str:
    if not state["rule_issues"]:
        return "llm_evaluator"
    if state["retry_count"] < MAX_REVISIONS:
        return "reviser"
    return "human_approval"


def route_after_evaluation(state: TravelState) -> str:
    if state["approved"]:
        return "human_approval"
    if state["retry_count"] < MAX_REVISIONS:
        return "reviser"
    return "human_approval"


def route_after_human(state: TravelState) -> str:
    if state["human_approved"]:
        return "finalize"
    if not state["human_feedback"]:
        return "finalize"
    if state["human_rounds"] > MAX_HUMAN_ROUNDS:
        return "finalize"
    return "feedback_router"


def route_after_feedback(state: TravelState) -> str:
    return RERUN_NODES.get(state["feedback_target"], "synthesizer")


def build_graph(include_research: bool = True, checkpointer=None):
    builder = StateGraph(TravelState)

    builder.add_node("budget_calculator", budget_calculator)
    builder.add_node("synthesizer", synthesizer)
    builder.add_node("rule_checks", rule_checks)
    builder.add_node("llm_evaluator", llm_evaluator)
    builder.add_node("reviser", reviser)
    builder.add_node("human_approval", human_approval)
    builder.add_node("feedback_router", feedback_router)
    builder.add_node("rerun_transport", transport_researcher)
    builder.add_node("rerun_accommodation", accommodation_researcher)
    builder.add_node("rerun_activities", activities_researcher)
    builder.add_node("finalize", finalize)

    if include_research:
        builder.add_node("planner", planner)
        builder.add_node("transport_researcher", transport_researcher)
        builder.add_node("accommodation_researcher", accommodation_researcher)
        builder.add_node("activities_researcher", activities_researcher)

        builder.add_edge(START, "planner")
        for researcher in RESEARCHERS:
            builder.add_edge("planner", researcher)
        builder.add_edge(RESEARCHERS, "budget_calculator")
    else:
        builder.add_edge(START, "synthesizer")

    builder.add_edge("budget_calculator", "synthesizer")
    builder.add_edge("synthesizer", "rule_checks")
    builder.add_conditional_edges(
        "rule_checks",
        route_after_rules,
        ["llm_evaluator", "reviser", "human_approval"],
    )
    builder.add_conditional_edges(
        "llm_evaluator",
        route_after_evaluation,
        ["reviser", "human_approval"],
    )
    builder.add_edge("reviser", "synthesizer")
    builder.add_conditional_edges(
        "human_approval",
        route_after_human,
        ["feedback_router", "finalize"],
    )
    builder.add_conditional_edges(
        "feedback_router",
        route_after_feedback,
        [*RERUN_NODES.values(), "synthesizer"],
    )
    for rerun_node in RERUN_NODES.values():
        builder.add_edge(rerun_node, "budget_calculator")
    builder.add_edge("finalize", END)

    return builder.compile(checkpointer=checkpointer)


connection = sqlite3.connect(CHECKPOINT_DB, check_same_thread=False)
checkpointer = SqliteSaver(connection)

graph = build_graph(checkpointer=checkpointer)
review_graph = build_graph(include_research=False, checkpointer=checkpointer)
