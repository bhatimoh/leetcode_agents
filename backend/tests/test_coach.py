"""Contest scoring used by the coach before it calls the model."""

from app.agents.coach import score_contests


def test_five_contests_mark_a_dropping_trend_and_missed_questions():
    performance = score_contests(
        [
            {"title": "Weekly Contest 5", "problems_solved": 1, "total_problems": 4},
            {"title": "Weekly Contest 4", "problems_solved": 2, "total_problems": 4},
            {"title": "Weekly Contest 3", "problems_solved": 3, "total_problems": 4},
            {"title": "Weekly Contest 2", "problems_solved": 4, "total_problems": 4},
            {"title": "Weekly Contest 1", "problems_solved": 4, "total_problems": 4},
        ]
    )
    assert performance["trend"] == "dropping"
    assert performance["missed"] == 6
    assert "1/4 in Weekly Contest 5" in performance["summary"]


def test_full_solves_are_steady():
    performance = score_contests(
        [
            {"title": "Weekly Contest 2", "problems_solved": 4, "total_problems": 4},
            {"title": "Weekly Contest 1", "problems_solved": 4, "total_problems": 4},
        ]
    )
    assert performance["trend"] == "steady"
    assert performance["missed"] == 0
