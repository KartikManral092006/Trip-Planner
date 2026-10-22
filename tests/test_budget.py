from app.nodes.budget import calculate_budget, item_total


def make_item(category="transport", amount=1000, quantity=1, per_person=True, is_estimate=True):
    return {
        "name": "test item",
        "category": category,
        "amount": amount,
        "quantity": quantity,
        "per_person": per_person,
        "source_url": None,
        "is_estimate": is_estimate,
    }


def test_per_person_item_is_multiplied_by_travelers():
    item = make_item(amount=2500, per_person=True)
    assert item_total(item, travelers=2) == 5000


def test_group_item_is_not_multiplied_by_travelers():
    item = make_item(category="accommodation", amount=3000, quantity=3, per_person=False)
    assert item_total(item, travelers=2) == 9000


def test_under_budget():
    items = [
        make_item("transport", amount=2500, per_person=True),
        make_item("accommodation", amount=3000, quantity=3, per_person=False),
        make_item("food", amount=800, quantity=4, per_person=True),
    ]
    summary = calculate_budget(items, travelers=2, budget=30000)

    assert summary["total"] == 5000 + 9000 + 6400
    assert summary["remaining"] == 30000 - 20400
    assert summary["over_budget"] is False
    assert summary["missing_categories"] == []


def test_over_budget():
    items = [make_item("transport", amount=9030, quantity=2, per_person=True)]
    summary = calculate_budget(items, travelers=2, budget=30000)

    assert summary["total"] == 36120
    assert summary["over_budget"] is True
    assert summary["remaining"] == -6120


def test_category_totals():
    items = [
        make_item("transport", amount=1000),
        make_item("transport", amount=500, per_person=False),
        make_item("activities", amount=200),
    ]
    summary = calculate_budget(items, travelers=2, budget=10000)

    assert summary["by_category"]["transport"] == 2500
    assert summary["by_category"]["activities"] == 400
    assert summary["by_category"]["food"] == 0


def test_empty_research_reports_missing_categories():
    summary = calculate_budget([], travelers=2, budget=30000)

    assert summary["total"] == 0
    assert summary["over_budget"] is False
    assert summary["missing_categories"] == ["transport", "accommodation", "food"]


def test_estimate_count():
    items = [make_item(is_estimate=True), make_item(is_estimate=False)]
    summary = calculate_budget(items, travelers=1, budget=10000)

    assert summary["estimate_count"] == 1