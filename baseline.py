import time
from datetime import date

from app.llm import llm
from app.sample_trip import SAMPLE_TRIP


def build_prompt(trip: dict) -> str:
    start = date.fromisoformat(trip["start_date"])
    end = date.fromisoformat(trip["end_date"])
    num_days = (end - start).days + 1

    return f"""
You are an expert travel planner. Create a practical, realistic
travel itinerary for the trip below.

TRIP DETAILS:
Departure city: {trip['origin']}
Destination: {trip['destination']}
Dates: {trip['start_date']} to {trip['end_date']} ({num_days} days)
Travelers: {trip['travelers']}
Total budget: {trip['budget']} {trip['currency']}
Interests: {', '.join(trip['interests'])}

PREFERENCES:
Accommodation type: {trip['accommodation_type']}
Preferred transport: {', '.join(trip['transport_preference'])}
Food preference: {trip['food_preference']}
Pace: {trip['pace']}
Special requirements: {trip['special_requirements'] or 'None'}

REQUIREMENTS:
- Organize the itinerary day by day, covering exactly {num_days} days.
- Include outbound and return transport from the departure city.
- Include accommodation and activities for each day.
- Provide a budget breakdown for transport, accommodation, food,
  activities, and other expenses, all in {trip['currency']}.
- Show per-person costs and total costs for all travelers separately.
- Calculate the estimated total and compare it with the budget.
- If the budget is not enough, explain the shortfall and suggest
  cheaper alternatives.
- Clearly label prices as estimates.
- Return the itinerary in readable Markdown.
"""


def run_baseline(trip: dict) -> tuple[str, float]:
    start_time = time.perf_counter()
    response = llm.invoke(build_prompt(trip))
    return response.text, time.perf_counter() - start_time


if __name__ == "__main__":
    itinerary, elapsed = run_baseline(SAMPLE_TRIP)

    print(itinerary)
    print(f"\n--- Generated in {elapsed:.1f} seconds ---")

    with open("baseline_output.md", "w", encoding="utf-8") as f:
        f.write(itinerary)
