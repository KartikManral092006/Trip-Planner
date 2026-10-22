import time
from pprint import pprint

from app.nodes.planner import planner
from app.sample_trip import SAMPLE_TRIP
from app.state import make_initial_state


state = make_initial_state(SAMPLE_TRIP)

start_time = time.perf_counter()
result = planner(state)
elapsed = time.perf_counter() - start_time

pprint(result, width=100)
print(f"\n--- Planner took {elapsed:.1f} seconds ---")