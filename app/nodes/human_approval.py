from langgraph.types import interrupt

from app.state import TravelState


def human_approval(state: TravelState) -> dict:
    decision = interrupt({
        "itinerary": state["itinerary"],
        "budget_summary": state["budget_summary"],
        "rule_issues": state["rule_issues"],
        "evaluation_feedback": state["evaluation_feedback"],
    })

    approved = bool(decision.get("approved", False))
    feedback = str(decision.get("feedback", "")).strip()

    if approved:
        return {"human_approved": True, "human_feedback": feedback}

    return {
        "human_approved": False,
        "human_feedback": feedback,
        "human_rounds": state["human_rounds"] + 1,
    }
