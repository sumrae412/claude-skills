from aggregate_reviewer_findings import aggregate_review_output


def test_aggregate_adds_blockers_for_sub_threshold_scores():
    registry = {
        "reviewers": [
            {
                "id": "adversarial-breaker",
                "score_threshold": 7,
                "scored_criteria": ["input_validation", "failure_modes"]
            }
        ]
    }
    review_output = {
        "reviewer": "adversarial-breaker",
        "scores": [
            {
                "criterion": "input_validation",
                "score": 5,
                "break_case": "Empty payload bypasses guard."
            },
            {
                "criterion": "failure_modes",
                "score": 8,
                "break_case": "Dependency timeout retried correctly."
            }
        ],
        "findings": []
    }

    aggregated = aggregate_review_output(review_output, registry)

    assert aggregated["aggregated_blockers"] == 1
    assert aggregated["findings"][0]["title"] == (
        "Adversarial score 5/10 on input_validation"
    )


def test_aggregate_leaves_unscored_reviewers_unchanged():
    registry = {"reviewers": [{"id": "plain-reviewer"}]}
    review_output = {"reviewer": "plain-reviewer", "findings": []}

    aggregated = aggregate_review_output(review_output, registry)

    assert aggregated == review_output


def test_aggregate_ignores_unknown_criteria():
    registry = {
        "reviewers": [
            {
                "id": "adversarial-breaker",
                "score_threshold": 7,
                "scored_criteria": ["input_validation"]
            }
        ]
    }
    review_output = {
        "reviewer": "adversarial-breaker",
        "scores": [
            {
                "criterion": "unknown",
                "score": 1,
                "break_case": "Ignored by registry."
            }
        ],
        "findings": []
    }

    aggregated = aggregate_review_output(review_output, registry)

    assert aggregated["aggregated_blockers"] == 0
    assert aggregated["findings"] == []
