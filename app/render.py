def itinerary_to_markdown(state: dict) -> str:
    itinerary = state["itinerary"]
    budget = state["budget_summary"]
    currency = state["currency"]
    lines = [f"# {itinerary['title']}", ""]

    for day in itinerary["days"]:
        travel = " (travel day)" if day["is_travel_day"] else ""
        lines.append(f"## Day {day['day']}: {day['date']}{travel}")
        lines.append(f"**Location:** {day['location']}")
        lines.append("")
        for activity in day["activities"]:
            lines.append(f"- {activity}")
        if day["stay"]:
            lines.append(f"\n**Stay:** {day['stay']}")
        lines.append("")

    lines += ["## Budget", "", "| Category | Amount |", "|---|---:|"]
    for category, amount in budget["by_category"].items():
        if amount:
            lines.append(f"| {category.title()} | {amount:,.0f} {currency} |")
    lines.append(f"| **Total** | **{budget['total']:,.0f} {currency}** |")
    lines.append(f"| Budget | {budget['budget']:,.0f} {currency} |")
    lines.append(f"| Remaining | {budget['remaining']:,.0f} {currency} |")
    lines.append("")
    lines.append(f"{budget['estimate_count']} of {len(budget['items'])} prices are estimates.")

    sections = {
        "Warnings": itinerary["warnings"],
        "Suggestions": itinerary["suggestions"],
        "Unresolved issues": state["rule_issues"],
    }
    for title, entries in sections.items():
        if entries:
            lines += ["", f"## {title}", ""]
            lines += [f"- {entry}" for entry in entries]

    return "\n".join(lines)
