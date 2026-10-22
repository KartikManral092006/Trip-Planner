import json
import sys
import time
import uuid

from langgraph.types import Command

from app.graph import graph, review_graph
from app.render import itinerary_to_markdown
from app.sample_trip import SAMPLE_TRIP
from app.state import REVIEW_DEFAULTS, make_initial_state


SAVED_STATE = "last_run.json"


def ask_for_decision() -> dict:
    if "--auto-approve" in sys.argv:
        print("Auto-approving.")
        return {"approved": True, "feedback": ""}

    answer = input("\nApprove this plan? (y/n): ").strip().lower()
    if answer == "y":
        return {"approved": True, "feedback": ""}

    feedback = input("What should change? ").strip()
    return {"approved": False, "feedback": feedback}


def get_option(name: str) -> str | None:
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return None


selected_graph = review_graph if "--review" in sys.argv else graph
resume_id = get_option("--resume")
thread_id = resume_id or str(uuid.uuid4())

config = {
    "configurable": {"thread_id": thread_id},
    "max_concurrency": 1,
}

if resume_id:
    state = dict(selected_graph.get_state(config).values)
    graph_input = None
elif "--review" in sys.argv:
    with open(SAVED_STATE, encoding="utf-8") as f:
        state = json.load(f)
    state.update(REVIEW_DEFAULTS)
    graph_input = state
else:
    state = make_initial_state(SAMPLE_TRIP)
    graph_input = state

start_time = time.perf_counter()


def run_until_done(graph_input) -> None:
    while True:
        stream_steps(graph_input)

        snapshot = selected_graph.get_state(config)
        if not snapshot.interrupts:
            return

        print()
        print(itinerary_to_markdown(state))
        graph_input = Command(resume=ask_for_decision())


def stream_steps(graph_input) -> None:
    for step in selected_graph.stream(graph_input, config=config, stream_mode="updates"):
        for node_name, update in step.items():
            if node_name == "__interrupt__":
                continue
            state.update(update)
            print(f"[{time.perf_counter() - start_time:5.1f}s] finished: {node_name}")

            if node_name == "rule_checks":
                for issue in state["rule_issues"]:
                    print(f"    rule issue: {issue}")
            if node_name == "llm_evaluator":
                print(f"    approved: {state['approved']}  {state['evaluation_feedback']}")
            if node_name == "feedback_router":
                print(f"    sending feedback to: {state['feedback_target']}")


try:
    run_until_done(graph_input)
except Exception as error:
    review_flag = " --review" if "--review" in sys.argv else ""
    print(f"\nFailed: {error}")
    print("Progress is saved after every step. Continue later with:")
    print(f"  uv run run_graph.py{review_flag} --resume {thread_id}")
    sys.exit(1)

with open(SAVED_STATE, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

markdown = itinerary_to_markdown(state)

with open("itinerary_output.md", "w", encoding="utf-8") as f:
    f.write(markdown)

print(f"\nStatus: {state['status']}   Revisions: {state['retry_count']}   "
      f"Feedback rounds: {state['human_rounds']}")
print("Saved to itinerary_output.md")
