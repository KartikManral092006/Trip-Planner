import re

from app.state import TravelState, trip_dates


MAX_TRAVEL_SHARE = 0.5
PACE_LIMITS = {"relaxed": 2, "moderate": 3, "packed": 5}
GENERIC_WORDS = {
    "hotel", "resort", "room", "rooms", "double", "standard", "deluxe", "near",
    "beach", "north", "south", "east", "west", "with", "star", "stay", "guest",
    "guests", "house", "night", "nights", "area", "city", "centre", "center",
}


def mentions(texts: list[str], words: list[str]) -> bool:
    joined = " ".join(texts).lower()
    return any(word in joined for word in words)


def total_travel_hours(budget_summary: dict) -> float:
    return sum(
        item.get("duration_hours") or 0
        for item in budget_summary["items"]
        if item["category"] == "transport"
    )


def name_words(text: str, ignore: set[str]) -> set[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return {word for word in words if len(word) > 3 and word not in ignore}


def stay_matches_research(stay: str, accommodation_names: list[str], ignore: set[str]) -> bool:
    stay_words = name_words(stay, ignore)
    return any(stay_words & name_words(name, ignore) for name in accommodation_names)


def check_itinerary(state: TravelState) -> list[str]:
    itinerary = state["itinerary"]
    budget = state["budget_summary"]
    currency = state["currency"]
    days = itinerary["days"]
    issues = []

    expected = trip_dates(state["start_date"], state["num_days"])
    if [day["date"] for day in days] != expected:
        issues.append(
            f"The itinerary must have exactly {len(expected)} days with these dates "
            f"in order: {', '.join(expected)}."
        )

    if budget["missing_categories"]:
        issues.append(
            f"Research is missing for: {', '.join(budget['missing_categories'])}. "
            "Add a warning that these costs are not included."
        )

    if budget["over_budget"]:
        over = -budget["remaining"]
        if not mentions(itinerary["warnings"], ["budget"]):
            issues.append(
                f"The plan is over budget by {over:,.0f} {currency}. Add a warning about it."
            )
        if not itinerary["suggestions"]:
            issues.append("The plan is over budget. Suggest concrete ways to save money.")

    travel_hours = total_travel_hours(budget)
    trip_hours = state["num_days"] * 24

    travel_days_needed = int(travel_hours // 24)
    travel_days = sum(1 for day in days if day["is_travel_day"])
    if travel_days < travel_days_needed:
        issues.append(
            f"Transport takes about {travel_hours:.0f} hours, which fills at least "
            f"{travel_days_needed} days, but only {travel_days} days are travel days. "
            "Do not schedule sightseeing while travelling."
        )

    if travel_hours > trip_hours * MAX_TRAVEL_SHARE:
        if not mentions(itinerary["warnings"], ["travel", "journey", "train", "flight"]):
            issues.append(
                f"Travel takes {travel_hours:.0f} of the {trip_hours} trip hours. "
                "Warn the traveler and suggest faster transport or a longer trip."
            )

    accommodation_names = [
        item["name"] for item in budget["items"] if item["category"] == "accommodation"
    ]
    ignore = GENERIC_WORDS | name_words(state["destination"], set())
    if accommodation_names:
        for day in days:
            stay = day["stay"]
            if stay and not stay_matches_research(stay, accommodation_names, ignore):
                short_names = [name.split(" (")[0] for name in accommodation_names]
                issues.append(
                    f"Day {day['day']} stays at '{stay}', which is not the researched "
                    f"accommodation: {'; '.join(short_names)}."
                )

    limit = PACE_LIMITS[state["pace"]]
    for day in days:
        if not day["is_travel_day"] and len(day["activities"]) > limit:
            issues.append(
                f"Day {day['day']} has {len(day['activities'])} activities, but a "
                f"{state['pace']} pace allows at most {limit}."
            )

    return issues


def rule_checks(state: TravelState) -> dict:
    return {"rule_issues": check_itinerary(state)}
