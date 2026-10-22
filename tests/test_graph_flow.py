from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

import app.graph as graph_module
from app.sample_trip import SAMPLE_TRIP
from app.state import make_initial_state


def item(category, amount):
    return {
        "name": f"Test {category}",
        "category": category,
        "amount": amount,
        "quantity": 1,
        "per_person": False,
        "source_url": None,
        "is_estimate": True,
        "duration_hours": None,
    }


def build_test_graph(monkeypatch, calls):
    def fake_researcher(category, state_key):
        def node(state):
            calls[category] = calls.get(category, 0) + 1
            return {state_key: {"summary": category, "items": [item(category, 1000)], "alternatives": []}}
        return node

    def fake_synthesizer(state):
        calls["synthesizer"] = calls.get("synthesizer", 0) + 1
        return {"itinerary": {"title": "Test", "days": [], "warnings": [], "suggestions": []}}

    def fake_router(state):
        target = "accommodation" if "hotel" in state["human_feedback"] else "itinerary_only"
        return {"feedback_target": target, "retry_count": 0, "approved": False}

    monkeypatch.setattr(graph_module, "planner", lambda state: {"research_plan": {}})
    monkeypatch.setattr(graph_module, "transport_researcher", fake_researcher("transport", "transport_research"))
    monkeypatch.setattr(graph_module, "accommodation_researcher", fake_researcher("accommodation", "accommodation_research"))
    monkeypatch.setattr(graph_module, "activities_researcher", fake_researcher("activities", "activities_research"))
    monkeypatch.setattr(graph_module, "synthesizer", fake_synthesizer)
    monkeypatch.setattr(graph_module, "rule_checks", lambda state: {"rule_issues": []})
    monkeypatch.setattr(graph_module, "llm_evaluator", lambda state: {"approved": True, "evaluation_feedback": ""})
    monkeypatch.setattr(graph_module, "feedback_router", fake_router)

    return graph_module.build_graph(checkpointer=InMemorySaver())


def test_plan_pauses_for_human_approval(monkeypatch):
    calls = {}
    graph = build_test_graph(monkeypatch, calls)
    config = {"configurable": {"thread_id": "pause"}}

    graph.invoke(make_initial_state(SAMPLE_TRIP), config=config)

    assert graph.get_state(config).interrupts
    assert calls == {"transport": 1, "accommodation": 1, "activities": 1, "synthesizer": 1}


def test_approval_finishes_the_trip(monkeypatch):
    graph = build_test_graph(monkeypatch, {})
    config = {"configurable": {"thread_id": "approve"}}

    graph.invoke(make_initial_state(SAMPLE_TRIP), config=config)
    result = graph.invoke(Command(resume={"approved": True}), config=config)

    assert result["status"] == "approved"
    assert not graph.get_state(config).interrupts


def test_hotel_feedback_reruns_only_accommodation(monkeypatch):
    calls = {}
    graph = build_test_graph(monkeypatch, calls)
    config = {"configurable": {"thread_id": "rerun"}}

    graph.invoke(make_initial_state(SAMPLE_TRIP), config=config)
    graph.invoke(Command(resume={"approved": False, "feedback": "find a cheaper hotel"}), config=config)

    assert graph.get_state(config).interrupts
    assert calls == {"transport": 1, "accommodation": 2, "activities": 1, "synthesizer": 2}


def test_rejection_without_feedback_ends_as_rejected(monkeypatch):
    graph = build_test_graph(monkeypatch, {})
    config = {"configurable": {"thread_id": "reject"}}

    graph.invoke(make_initial_state(SAMPLE_TRIP), config=config)
    result = graph.invoke(Command(resume={"approved": False, "feedback": ""}), config=config)

    assert result["status"] == "rejected"
