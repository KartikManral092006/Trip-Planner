from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import runner
from app.api.schemas import TripRequest
from main import app


client = TestClient(app)


def trip_payload(**changes):
    start = date.today() + timedelta(days=30)
    payload = {
        "origin": "Dehradun",
        "destination": "Goa",
        "start_date": start.isoformat(),
        "end_date": (start + timedelta(days=3)).isoformat(),
        "budget": 30000,
        "travelers": 2,
        "interests": ["beaches", " food ", "beaches"],
        "transport_preference": ["train", "flight"],
    }
    payload.update(changes)
    return payload


def test_valid_trip_is_cleaned():
    request = TripRequest(**trip_payload(currency="inr"))
    assert request.interests == ["beaches", "food"]
    assert request.currency == "INR"
    assert request.to_trip()["start_date"] == trip_payload()["start_date"]


@pytest.mark.parametrize("changes", [
    {"destination": "dehradun"},
    {"start_date": "2020-01-01", "end_date": "2020-01-03"},
    {"end_date": (date.today() + timedelta(days=10)).isoformat()},
    {"end_date": (date.today() + timedelta(days=60)).isoformat()},
    {"travelers": 0},
    {"budget": -5},
    {"interests": ["  "]},
    {"transport_preference": ["rocket"]},
    {"pace": "fast"},
])
def test_invalid_trips_are_rejected(changes):
    with pytest.raises(ValidationError):
        TripRequest(**trip_payload(**changes))


def test_create_trip_returns_immediately(monkeypatch):
    started = []
    monkeypatch.setattr(runner, "start_trip", lambda thread_id, trip: started.append(trip))

    response = client.post("/trips", json=trip_payload())

    assert response.status_code == 202
    assert response.json()["status"] == "running"
    assert started[0]["destination"] == "Goa"


def test_invalid_trip_returns_422():
    response = client.post("/trips", json=trip_payload(travelers=0))
    assert response.status_code == 422


def test_unknown_trip_returns_404(monkeypatch):
    monkeypatch.setattr(runner, "get_trip", lambda thread_id: None)
    assert client.get("/trips/unknown").status_code == 404


def test_approval_requires_waiting_trip(monkeypatch):
    monkeypatch.setattr(runner, "get_trip", lambda thread_id: {"status": "running"})
    response = client.post("/trips/abc/approval", json={"approved": True})
    assert response.status_code == 409


def test_approval_resumes_trip(monkeypatch):
    resumed = []
    monkeypatch.setattr(runner, "get_trip", lambda thread_id: {"status": "waiting_for_approval"})
    monkeypatch.setattr(runner, "resume_trip", lambda thread_id, decision: resumed.append(decision))

    response = client.post("/trips/abc/approval", json={"approved": False, "feedback": "cheaper hotel"})

    assert response.status_code == 202
    assert resumed == [{"approved": False, "feedback": "cheaper hotel"}]


def test_retry_requires_failed_trip(monkeypatch):
    monkeypatch.setattr(runner, "get_trip", lambda thread_id: {"status": "approved"})
    assert client.post("/trips/abc/retry").status_code == 409


def test_retry_continues_failed_trip(monkeypatch):
    retried = []
    monkeypatch.setattr(runner, "get_trip", lambda thread_id: {"status": "failed"})
    monkeypatch.setattr(runner, "retry_trip", lambda thread_id: retried.append(thread_id))

    response = client.post("/trips/abc/retry")

    assert response.status_code == 202
    assert retried == ["abc"]


def test_allowed_origins_default_to_local_frontends(monkeypatch):
    from main import allowed_origins

    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    assert "http://localhost:5173" in allowed_origins()


def test_allowed_origins_come_from_environment(monkeypatch):
    from main import allowed_origins

    monkeypatch.setenv("ALLOWED_ORIGINS", "https://trip-planner.vercel.app/, https://example.com")
    assert allowed_origins() == ["https://trip-planner.vercel.app", "https://example.com"]


def test_local_frontend_passes_cors():
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
