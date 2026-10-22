import time

from app.nodes.planner import planner
from app.nodes.researchers import transport_researcher
from app.sample_trip import SAMPLE_TRIP
from app.state import make_initial_state


state = make_initial_state(SAMPLE_TRIP)
state.update(planner(state))

start_time = time.perf_counter()
result = transport_researcher(state)
elapsed = time.perf_counter() - start_time

research = result["transport_research"]

print("SUMMARY:")
print(research["summary"])
print("\nITEMS:")

for item in research["items"]:
    unit = "per person" if item["per_person"] else "per group"
    label = "estimate" if item["is_estimate"] else "sourced"
    print(f"- {item['name']}")
    print(f"  {item['amount']} x {item['quantity']} ({unit}, {label})")
    print(f"  {item['source_url'] or 'NO SOURCE'}")

sourced = sum(1 for item in research["items"] if item["source_url"])
print(f"\n{sourced}/{len(research['items'])} items have a source URL")
print(f"--- Transport research took {elapsed:.1f} seconds ---")