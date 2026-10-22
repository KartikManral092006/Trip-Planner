from app.state import TravelState


def reviser(state: TravelState) -> dict:
    return {"retry_count": state["retry_count"] + 1}


def finalize(state: TravelState) -> dict:
    status = "approved" if state["human_approved"] else "rejected"
    return {"status": status}
