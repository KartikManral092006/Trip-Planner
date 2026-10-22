import json

from app.llm import llm
from app.nodes.budget import RESEARCH_KEYS, item_total
from app.prompts.synthesizer_prompt import SYNTHESIZER_PROMPT
from app.prompts.trip_details import format_trip_details
from app.schemas.itinerary import Itinerary
from app.state import TravelState, trip_dates


MAX_SUMMARY_CHARS = 1500

RESEARCH_SECTIONS = {
    "TRANSPORT": "transport_research",
    "ACCOMMODATION": "accommodation_research",
    "ACTIVITIES AND FOOD": "activities_research",
}


structured_llm = llm.with_structured_output(Itinerary)


def format_research(state: TravelState) -> str:
    sections = []
    for title, key in RESEARCH_SECTIONS.items():
        research = state[key] or {"summary": "No research available."}
        sections.append(f"{title}:\n{research['summary'][:MAX_SUMMARY_CHARS]}")
    return "\n\n".join(sections)


def format_budget(state: TravelState) -> str:
    budget = state["budget_summary"]
    currency = state["currency"]
    lines = []

    for item in budget["items"]:
        line = f"- [{item['category']}] {item['name']}: {item['total']:,.0f} {currency}"
        if item.get("duration_hours"):
            line += f" (journey time: {item['duration_hours']} hours)"
        lines.append(line)

    lines.append(f"Total: {budget['total']:,.0f} {currency}")
    lines.append(f"Budget: {budget['budget']:,.0f} {currency}")

    if budget["over_budget"]:
        lines.append(f"OVER BUDGET by {-budget['remaining']:,.0f} {currency}")
    else:
        lines.append(f"Remaining: {budget['remaining']:,.0f} {currency}")

    alternatives = format_alternatives(state)
    if alternatives:
        lines.append("\nALTERNATIVES (not in the total, use them for suggestions):")
        lines.extend(alternatives)

    return "\n".join(lines)


def format_alternatives(state: TravelState) -> list[str]:
    lines = []
    for key in RESEARCH_KEYS:
        research = state[key] or {}
        for item in research.get("alternatives", []):
            total = item_total(item, state["travelers"])
            lines.append(f"- [{item['category']}] {item['name']}: {total:,.0f} {state['currency']}")
    return lines


def format_feedback(state: TravelState) -> str:
    if state["itinerary"] is None:
        return "None. This is the first draft."

    issues = "\n".join(f"- {issue}" for issue in state["rule_issues"])
    return f"""
PREVIOUS DRAFT:
{json.dumps(state['itinerary'])}

ISSUES FOUND BY CODE:
{issues or 'None'}

REVIEWER FEEDBACK:
{state['evaluation_feedback'] or 'None'}

TRAVELER FEEDBACK (most important):
{state['human_feedback'] or 'None'}
"""


def synthesizer(state: TravelState) -> dict:
    request = f"""
TRIP DETAILS:
{format_trip_details(state)}

TRIP DATES:
{', '.join(trip_dates(state['start_date'], state['num_days']))}

RESEARCH:
{format_research(state)}

BUDGET (calculated in code):
{format_budget(state)}

REVIEW FEEDBACK:
{format_feedback(state)}
"""

    itinerary = structured_llm.invoke([
        ("system", SYNTHESIZER_PROMPT),
        ("human", request),
    ])

    if itinerary is None:
        raise RuntimeError("Synthesizer returned no itinerary.")

    return {"itinerary": itinerary.model_dump()}
