from app.nodes.researchers import run_research
from app.sample_trip import SAMPLE_TRIP
from app.state import make_initial_state


class FailingAgent:
    def invoke(self, request):
        raise RuntimeError("rate limit")


def test_failed_first_run_reports_unavailable():
    result = run_research(FailingAgent(), make_initial_state(SAMPLE_TRIP), ["task"])

    assert result["items"] == []
    assert "unavailable" in result["summary"]


def test_failed_rerun_keeps_previous_research():
    previous = {"summary": "Train via Delhi", "items": [{"name": "train"}], "alternatives": []}
    result = run_research(FailingAgent(), make_initial_state(SAMPLE_TRIP), ["task"], previous)

    assert result["items"] == [{"name": "train"}]
    assert "Update failed (rate limit)" in result["summary"]
