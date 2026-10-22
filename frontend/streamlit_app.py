import os
import time
from datetime import date, timedelta

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
POLL_SECONDS = 4

STEP_LABELS = {
    "planner": "Planning the research",
    "transport_researcher": "Researching transport",
    "accommodation_researcher": "Researching places to stay",
    "activities_researcher": "Researching activities and food",
    "budget_calculator": "Calculating the budget",
    "synthesizer": "Writing the itinerary",
    "rule_checks": "Checking the plan",
    "llm_evaluator": "Reviewing quality",
    "reviser": "Revising the plan",
    "feedback_router": "Reading your feedback",
    "rerun_transport": "Finding new transport options",
    "rerun_accommodation": "Finding new places to stay",
    "rerun_activities": "Finding new activities",
    "human_approval": "Preparing the plan for you",
    "finalize": "Finishing",
}


def call_api(method: str, path: str, **kwargs) -> requests.Response:
    try:
        return requests.request(method, f"{API_URL}{path}", timeout=30, **kwargs)
    except requests.ConnectionError:
        st.error(f"Cannot reach the API at {API_URL}. Start it with: uv run uvicorn main:app")
        st.stop()


def show_errors(response: requests.Response) -> None:
    detail = response.json().get("detail", response.text)
    if isinstance(detail, list):
        for error in detail:
            field = " → ".join(str(part) for part in error["loc"][1:]) or "trip"
            st.error(f"{field}: {error['msg'].removeprefix('Value error, ')}")
    else:
        st.error(detail)


def reset() -> None:
    st.session_state.pop("thread_id", None)


def show_form() -> None:
    st.title("AI Travel Planner")
    st.caption("Agents research your trip, code checks the budget, and you approve the plan.")

    with st.form("trip"):
        left, right = st.columns(2)
        origin = left.text_input("From", "Dehradun")
        destination = right.text_input("To", "Goa")
        start_date = left.date_input("Start date", date.today() + timedelta(days=30))
        end_date = right.date_input("End date", date.today() + timedelta(days=33))
        budget = left.number_input("Total budget", min_value=1000, value=30000, step=1000)
        currency = right.text_input("Currency", "INR", max_chars=3)
        travelers = left.number_input("Travelers", min_value=1, max_value=20, value=2)
        pace = right.selectbox("Pace", ["relaxed", "moderate", "packed"], index=1)
        accommodation = left.selectbox("Stay", ["any", "hotel", "hostel", "homestay"], index=1)
        food = right.selectbox(
            "Food", ["no preference", "vegetarian", "non-vegetarian", "vegan"]
        )
        interests = st.text_input("Interests (comma-separated)", "beaches, food, nightlife")
        transport = st.multiselect(
            "Transport", ["train", "flight", "bus", "car"], default=["train", "flight"]
        )
        special = st.text_area("Special requirements", "")
        submitted = st.form_submit_button("Plan my trip", type="primary")

    if not submitted:
        return

    payload = {
        "origin": origin,
        "destination": destination,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "budget": budget,
        "travelers": travelers,
        "interests": [part.strip() for part in interests.split(",")],
        "currency": currency,
        "accommodation_type": accommodation,
        "transport_preference": transport,
        "food_preference": food,
        "pace": pace,
        "special_requirements": special,
    }

    response = call_api("post", "/trips", json=payload)
    if response.status_code == 202:
        st.session_state.thread_id = response.json()["thread_id"]
        st.rerun()
    show_errors(response)


def show_budget(trip: dict) -> None:
    budget = trip["budget_summary"]
    rows = [
        {
            "Item": item["name"],
            "Category": item["category"],
            "Total": round(item["total"]),
            "Price": "estimate" if item["is_estimate"] else "sourced",
            "Source": item["source_url"],
        }
        for item in budget["items"]
    ]

    with st.expander(f"Budget details ({len(rows)} items)"):
        st.dataframe(
            rows,
            hide_index=True,
            column_config={"Source": st.column_config.LinkColumn("Source")},
        )


def show_review_notes(trip: dict) -> None:
    if not trip["rule_issues"] and not trip["evaluation_feedback"]:
        return

    with st.expander("Review notes"):
        for issue in trip["rule_issues"]:
            st.write(f"- Code check: {issue}")
        if trip["evaluation_feedback"]:
            st.write(f"- Reviewer: {trip['evaluation_feedback']}")


def send_decision(thread_id: str, approved: bool, feedback: str = "") -> None:
    response = call_api(
        "post",
        f"/trips/{thread_id}/approval",
        json={"approved": approved, "feedback": feedback},
    )
    if response.status_code == 202:
        st.rerun()
    show_errors(response)


def show_approval(thread_id: str) -> None:
    st.subheader("Your decision")
    feedback = st.text_area(
        "What should change?",
        placeholder="e.g. Find a cheaper hotel near Baga, or use flights instead of the train",
    )
    left, right = st.columns(2)

    if left.button("Approve plan", type="primary", use_container_width=True):
        send_decision(thread_id, approved=True)

    if right.button("Request changes", use_container_width=True):
        if feedback.strip():
            send_decision(thread_id, approved=False, feedback=feedback)
        else:
            st.warning("Describe what should change first.")


def show_trip(thread_id: str) -> None:
    response = call_api("get", f"/trips/{thread_id}")
    if response.status_code == 404:
        st.warning("This trip no longer exists.")
        reset()
        return

    trip = response.json()
    status = trip["status"]

    st.button("Plan another trip", on_click=reset)

    if status == "running":
        steps = [STEP_LABELS.get(step, step) for step in trip["next_steps"]]
        st.info(f"{', '.join(steps) or 'Starting'}… This can take a few minutes.")
        st.caption("Free-tier rate limits make each step wait between calls.")
        time.sleep(POLL_SECONDS)
        st.rerun()

    if status == "failed":
        st.error(f"The planner failed: {trip['error']}")
        st.caption("Progress is saved after every step, so a retry continues where it stopped.")
        if st.button("Retry", type="primary"):
            response = call_api("post", f"/trips/{thread_id}/retry")
            if response.status_code == 202:
                st.rerun()
            show_errors(response)
        return

    if status == "approved":
        st.success("Plan approved.")
    elif status == "rejected":
        st.warning("Plan rejected.")

    st.markdown(trip["itinerary_markdown"])
    show_budget(trip)
    show_review_notes(trip)

    if status == "waiting_for_approval":
        show_approval(thread_id)
    else:
        st.download_button(
            "Download itinerary (Markdown)",
            trip["itinerary_markdown"],
            file_name="itinerary.md",
        )


st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")

if "thread_id" in st.session_state:
    show_trip(st.session_state.thread_id)
else:
    show_form()
