from app.nodes.rule_checks import check_itinerary


def make_day(day, date, activities=None, is_travel_day=False):
    return {
        "day": day,
        "date": date,
        "location": "Goa",
        "is_travel_day": is_travel_day,
        "activities": activities if activities is not None else ["Beach walk"],
        "stay": "Sunrise Inn, Candolim",
    }


def make_state(days=None, over_budget=False, transport_hours=6, warnings=None,
               suggestions=None, missing=None, pace="moderate"):
    if days is None:
        days = [
            make_day(1, "2026-12-10"),
            make_day(2, "2026-12-11"),
            make_day(3, "2026-12-12"),
            make_day(4, "2026-12-13"),
        ]

    return {
        "destination": "Goa",
        "start_date": "2026-12-10",
        "num_days": 4,
        "currency": "INR",
        "pace": pace,
        "itinerary": {
            "title": "Test trip",
            "days": days,
            "warnings": warnings or [],
            "suggestions": suggestions or [],
        },
        "budget_summary": {
            "items": [
                {"name": "Train", "category": "transport", "duration_hours": transport_hours},
                {"name": "Sunrise Inn Candolim (3-star)", "category": "accommodation", "duration_hours": None},
            ],
            "over_budget": over_budget,
            "remaining": -4460 if over_budget else 1000,
            "missing_categories": missing or [],
        },
    }


def test_valid_itinerary_has_no_issues():
    assert check_itinerary(make_state()) == []


def test_missing_day_is_reported():
    days = [make_day(1, "2026-12-10"), make_day(2, "2026-12-11"), make_day(3, "2026-12-12")]
    issues = check_itinerary(make_state(days=days))
    assert any("exactly 4 days" in issue for issue in issues)


def test_wrong_date_is_reported():
    days = [
        make_day(1, "2026-12-10"),
        make_day(2, "2026-12-11"),
        make_day(3, "2026-12-12"),
        make_day(4, "2026-12-14"),
    ]
    issues = check_itinerary(make_state(days=days))
    assert any("2026-12-13" in issue for issue in issues)


def test_over_budget_without_warning_is_reported():
    issues = check_itinerary(make_state(over_budget=True))
    assert any("over budget by 4,460 INR" in issue for issue in issues)
    assert any("save money" in issue for issue in issues)


def test_over_budget_with_warning_and_suggestion_passes():
    state = make_state(
        over_budget=True,
        warnings=["The plan is over budget by 4,460 INR."],
        suggestions=["Choose a cheaper hotel."],
    )
    assert check_itinerary(state) == []


def test_missing_research_is_reported():
    issues = check_itinerary(make_state(missing=["food"]))
    assert any("missing for: food" in issue for issue in issues)


def test_long_journey_needs_travel_days():
    issues = check_itinerary(make_state(transport_hours=72))
    assert any("fills at least 3 days" in issue for issue in issues)


def test_long_journey_needs_warning():
    issues = check_itinerary(make_state(transport_hours=72))
    assert any("72 of the 96 trip hours" in issue for issue in issues)


def test_long_journey_with_travel_days_and_warning_passes():
    days = [
        make_day(1, "2026-12-10", activities=[], is_travel_day=True),
        make_day(2, "2026-12-11", activities=[], is_travel_day=True),
        make_day(3, "2026-12-12"),
        make_day(4, "2026-12-13", activities=[], is_travel_day=True),
    ]
    state = make_state(
        days=days,
        transport_hours=72,
        warnings=["The train journey takes 36 hours each way."],
    )
    assert check_itinerary(state) == []


def test_too_many_activities_for_pace():
    days = [
        make_day(1, "2026-12-10", activities=["a", "b", "c"]),
        make_day(2, "2026-12-11"),
        make_day(3, "2026-12-12"),
        make_day(4, "2026-12-13"),
    ]
    issues = check_itinerary(make_state(days=days, pace="relaxed"))
    assert any("Day 1 has 3 activities" in issue for issue in issues)


def test_stay_not_in_research_is_reported():
    days = [
        make_day(1, "2026-12-10"),
        make_day(2, "2026-12-11"),
        make_day(3, "2026-12-12"),
        make_day(4, "2026-12-13"),
    ]
    days[1]["stay"] = "Vintage Beach Resort, Agonda"
    issues = check_itinerary(make_state(days=days))
    assert any("Day 2 stays at 'Vintage Beach Resort, Agonda'" in issue for issue in issues)


def test_no_stay_on_last_night_is_fine():
    days = [
        make_day(1, "2026-12-10"),
        make_day(2, "2026-12-11"),
        make_day(3, "2026-12-12"),
        make_day(4, "2026-12-13"),
    ]
    days[3]["stay"] = None
    assert check_itinerary(make_state(days=days)) == []
