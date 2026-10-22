import json
import sys
import time
import uuid
from pathlib import Path

from baseline import run_baseline
from app.graph import graph
from app.state import make_initial_state
from eval.metrics import baseline_metrics, graph_metrics


EVAL_DIR = Path(__file__).parent
TRIPS_FILE = EVAL_DIR / "trips.json"
RESULTS_JSON = EVAL_DIR / "results.json"
RESULTS_MD = EVAL_DIR / "results.md"


def get_limit() -> int | None:
    if "--limit" in sys.argv:
        return int(sys.argv[sys.argv.index("--limit") + 1])
    return None


def evaluate_baseline(trip: dict, num_days: int) -> dict:
    text, seconds = run_baseline(trip)
    return {"seconds": round(seconds, 1), **baseline_metrics(text, num_days)}


def evaluate_graph(trip: dict) -> dict:
    config = {
        "configurable": {"thread_id": f"eval-{uuid.uuid4()}"},
        "max_concurrency": 1,
    }

    start_time = time.perf_counter()
    state = graph.invoke(make_initial_state(trip), config=config)
    seconds = time.perf_counter() - start_time

    return {"seconds": round(seconds, 1), **graph_metrics(state)}


def safely(function, *args) -> dict:
    try:
        return function(*args)
    except Exception as error:
        return {"error": str(error)}


def percent(results: list[dict], key: str) -> str:
    valid = [result for result in results if "error" not in result]
    if not valid:
        return "n/a"
    return f"{100 * sum(1 for result in valid if result[key]) / len(valid):.0f}%"


def average(results: list[dict], key: str) -> str:
    values = [result[key] for result in results if "error" not in result]
    if not values:
        return "n/a"
    return f"{sum(values) / len(values):.1f}"


def write_report(rows: list[dict]) -> None:
    baselines = [row["baseline"] for row in rows]
    graphs = [row["graph"] for row in rows]

    lines = [
        "# Evaluation results",
        "",
        f"{len(rows)} trips. The graph is measured at the point it asks for human approval.",
        "",
        "## Summary",
        "",
        "| Metric | Baseline (1 prompt) | Multi-agent graph |",
        "|---|---|---|",
        f"| Correct day-by-day dates | {percent(baselines, 'days_correct')} | {percent(graphs, 'days_correct')} |",
        f"| Avg. source URLs per plan | {average(baselines, 'source_urls')} | {average(graphs, 'source_urls')} |",
        f"| Avg. seconds per plan | {average(baselines, 'seconds')} | {average(graphs, 'seconds')} |",
        f"| Budget total calculated in code | no | yes |",
        f"| Over-budget plans that warn the user | manual check | {percent(graphs, 'budget_warning')} |",
        f"| Plans with no open rule issues | not checked | {percent([{**g, 'clean': g.get('open_rule_issues') == 0} for g in graphs], 'clean')} |",
        "",
        "## Per trip",
        "",
        "| Trip | Baseline days OK | Baseline URLs | Graph days OK | Graph URLs | Total | Budget | Over | Open issues | Revisions | Graph s |",
        "|---|---|---|---|---|---:|---:|---|---:|---:|---:|",
    ]

    for row in rows:
        trip, base, multi = row["trip"], row["baseline"], row["graph"]
        name = f"{trip['origin']} → {trip['destination']}"
        if "error" in multi:
            lines.append(f"| {name} | {base.get('days_correct', 'error')} | {base.get('source_urls', '-')} | error: {multi['error'][:60]} |||||||")
            continue
        lines.append(
            f"| {name} | {base.get('days_correct', 'error')} | {base.get('source_urls', '-')} | "
            f"{multi['days_correct']} | {multi['source_urls']} | {multi['total']:,.0f} | "
            f"{trip['budget']:,.0f} | {multi['over_budget']} | {multi['open_rule_issues']} | "
            f"{multi['revisions']} | {multi['seconds']} |"
        )

    lines += [
        "",
        "## Manual checks (fill in by hand)",
        "",
        "Automatic metrics cannot tell whether a price is true. For 3 trips:",
        "",
        "1. Add up the baseline's listed costs. Does its stated total match?",
        "2. Open 3 graph source URLs. Does the page show that price for that route or hotel?",
        "3. Note any place that does not exist or is in the wrong city.",
    ]

    RESULTS_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    trips = json.loads(TRIPS_FILE.read_text(encoding="utf-8"))[:get_limit()]
    rows = []

    for number, trip in enumerate(trips, start=1):
        name = f"{trip['origin']} → {trip['destination']}"
        num_days = make_initial_state(trip)["num_days"]

        print(f"[{number}/{len(trips)}] {name}: baseline...")
        baseline = safely(evaluate_baseline, trip, num_days)

        print(f"[{number}/{len(trips)}] {name}: multi-agent graph...")
        multi_agent = safely(evaluate_graph, trip)

        rows.append({"trip": trip, "baseline": baseline, "graph": multi_agent})
        RESULTS_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        write_report(rows)

    print(f"Done. See {RESULTS_MD}")


if __name__ == "__main__":
    main()
