from eval.metrics import baseline_metrics


def test_baseline_with_all_days_and_links():
    text = """
## Day 1: Arrive
Book at https://example.com/hotel (estimate)
## Day 2: Beach
## Day 3: Return, see https://example.com/train.
"""
    metrics = baseline_metrics(text, num_days=3)

    assert metrics["days_correct"] is True
    assert metrics["source_urls"] == 2
    assert metrics["labels_estimates"] is True


def test_baseline_with_missing_day():
    metrics = baseline_metrics("Day 1 ... Day 2 ...", num_days=3)
    assert metrics["days_correct"] is False
    assert metrics["source_urls"] == 0
