"""Contest scores passed to the model stay unchanged."""

from app.agents.nodes.finish import build_facts


def test_facts_include_questions_solved_in_recent_contests():
    facts = build_facts(
        "lee",
        {
            "acceptance_rate": 50,
            "solved": {"easy": 1, "medium": 2, "hard": 0},
            "all_tags": [],
        },
        {
            "attended": 2,
            "rating": 1500,
            "recent": [
                {"title": "Weekly Contest 9", "problems_solved": 1, "total_problems": 4},
                {"title": "Weekly Contest 8", "problems_solved": 3, "total_problems": 4},
            ],
        },
        [],
    )
    assert facts["recent_contests"][0]["problems_solved"] == 1
    assert facts["recent_contests"][0]["total_problems"] == 4
    assert facts["recent_contests"][1]["title"] == "Weekly Contest 8"
