import re

from app.nodes.rule_checks import check_itinerary, mentions
from app.state import trip_dates


def baseline_metrics(text: str, num_days: int) -> dict:
    day_numbers = {int(number) for number in re.findall(r"\bday\s*(\d{1,2})\b", text.lower())}
    urls = set(re.findall(r"https?://[^\s)\]>]+", text))

    return {
        "days_correct": day_numbers == set(range(1, num_days + 1)),
        "source_urls": len(urls),
        "labels_estimates": "estimate" in text.lower(),
    }


def graph_metrics(state: dict) -> dict:
    itinerary = state["itinerary"]
    budget = state["budget_summary"]
    items = budget["items"]
    expected = trip_dates(state["start_date"], state["num_days"])

    return {
        "days_correct": [day["date"] for day in itinerary["days"]] == expected,
        "source_urls": len({item["source_url"] for item in items if item["source_url"]}),
        "items": len(items),
        "sourced_items": sum(1 for item in items if item["source_url"]),
        "estimate_items": budget["estimate_count"],
        "total": budget["total"],
        "over_budget": budget["over_budget"],
        "budget_warning": (not budget["over_budget"]) or mentions(itinerary["warnings"], ["budget"]),
        "missing_categories": budget["missing_categories"],
        "open_rule_issues": len(check_itinerary(state)),
        "evaluator_approved": state["approved"],
        "revisions": state["retry_count"],
    }
