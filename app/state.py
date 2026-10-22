from datetime import date, timedelta
from typing import Literal, TypedDict


AccommodationType = Literal["hotel", "hostel", "homestay", "any"]
FoodPreference = Literal["vegetarian", "non-vegetarian", "vegan", "no preference"]
Pace = Literal["relaxed", "moderate", "packed"]
TripStatus = Literal[
    "running",
    "waiting_for_approval",
    "approved",
    "rejected",
    "failed",
]


class TravelState(TypedDict):
    origin: str
    destination: str
    start_date: str
    end_date: str
    num_days: int
    budget: float
    travelers: int
    interests: list[str]
    currency: str
    accommodation_type: AccommodationType
    transport_preference: list[str]
    food_preference: FoodPreference
    pace: Pace
    special_requirements: str

    research_plan: dict | None

    transport_research: dict | None
    accommodation_research: dict | None
    activities_research: dict | None

    budget_summary: dict | None

    itinerary: dict | None

    rule_issues: list[str]
    evaluation_feedback: str
    approved: bool
    retry_count: int

    human_approved: bool
    human_feedback: str
    feedback_target: str
    human_rounds: int

    status: TripStatus


REVIEW_DEFAULTS = {
    "itinerary": None,
    "rule_issues": [],
    "evaluation_feedback": "",
    "approved": False,
    "retry_count": 0,
    "human_approved": False,
    "human_feedback": "",
    "feedback_target": "",
    "human_rounds": 0,
    "status": "running",
}


def make_initial_state(trip: dict) -> TravelState:
    start = date.fromisoformat(trip["start_date"])
    end = date.fromisoformat(trip["end_date"])

    return {
        **trip,
        "num_days": (end - start).days + 1,
        "research_plan": None,
        "transport_research": None,
        "accommodation_research": None,
        "activities_research": None,
        "budget_summary": None,
        **REVIEW_DEFAULTS,
    }


def trip_dates(start_date: str, num_days: int) -> list[str]:
    start = date.fromisoformat(start_date)
    return [(start + timedelta(days=offset)).isoformat() for offset in range(num_days)]
