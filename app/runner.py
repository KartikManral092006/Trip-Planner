import logging

from langgraph.types import Command

from app.graph import graph
from app.render import itinerary_to_markdown
from app.state import make_initial_state


logger = logging.getLogger(__name__)

TRIP_FIELDS = ["origin", "destination", "start_date", "end_date", "travelers", "currency"]

running: set[str] = set()
errors: dict[str, str] = {}


def make_config(thread_id: str) -> dict:
    return {
        "configurable": {"thread_id": thread_id},
        "max_concurrency": 1,
    }


def mark_running(thread_id: str) -> None:
    running.add(thread_id)
    errors.pop(thread_id, None)


def run_graph(thread_id: str, graph_input) -> None:
    try:
        graph.invoke(graph_input, config=make_config(thread_id))
    except Exception as error:
        logger.exception("Trip %s failed", thread_id)
        errors[thread_id] = str(error)
    finally:
        running.discard(thread_id)


def start_trip(thread_id: str, trip: dict) -> None:
    run_graph(thread_id, make_initial_state(trip))


def resume_trip(thread_id: str, decision: dict) -> None:
    run_graph(thread_id, Command(resume=decision))


def retry_trip(thread_id: str) -> None:
    run_graph(thread_id, None)


def get_trip(thread_id: str) -> dict | None:
    snapshot = graph.get_state(make_config(thread_id))
    values = snapshot.values

    if thread_id in running:
        status = "running"
    elif thread_id in errors:
        status = "failed"
    elif not values:
        return None
    elif snapshot.interrupts:
        status = "waiting_for_approval"
    else:
        status = values["status"]

    has_plan = bool(values.get("itinerary") and values.get("budget_summary"))

    return {
        "thread_id": thread_id,
        "status": status,
        "error": errors.get(thread_id),
        "next_steps": list(snapshot.next),
        "trip": {key: values.get(key) for key in TRIP_FIELDS},
        "itinerary": values.get("itinerary"),
        "itinerary_markdown": itinerary_to_markdown(values) if has_plan else None,
        "budget_summary": values.get("budget_summary"),
        "rule_issues": values.get("rule_issues", []),
        "evaluation_feedback": values.get("evaluation_feedback", ""),
        "revisions": values.get("retry_count", 0),
        "feedback_rounds": values.get("human_rounds", 0),
    }
