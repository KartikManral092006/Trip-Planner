from app.state import TravelState


CATEGORIES = ["transport", "accommodation", "activities", "food", "other"]
REQUIRED_CATEGORIES = ["transport", "accommodation", "food"]
RESEARCH_KEYS = ["transport_research", "accommodation_research", "activities_research"]


def item_total(item: dict, travelers: int) -> float:
    people = travelers if item["per_person"] else 1
    return item["amount"] * item["quantity"] * people


def calculate_budget(items: list[dict], travelers: int, budget: float) -> dict:
    by_category = {category: 0.0 for category in CATEGORIES}
    lines = []

    for item in items:
        total = round(item_total(item, travelers), 2)
        by_category[item["category"]] += total
        lines.append({**item, "total": total})

    total = round(sum(by_category.values()), 2)

    return {
        "items": lines,
        "by_category": by_category,
        "total": total,
        "budget": budget,
        "remaining": round(budget - total, 2),
        "over_budget": total > budget,
        "estimate_count": sum(1 for item in items if item["is_estimate"]),
        "missing_categories": [
            category for category in REQUIRED_CATEGORIES if by_category[category] == 0
        ],
    }


def budget_calculator(state: TravelState) -> dict:
    items = []

    for key in RESEARCH_KEYS:
        research = state[key]
        if research:
            items.extend(research["items"])

    summary = calculate_budget(items, state["travelers"], state["budget"])
    return {"budget_summary": summary}