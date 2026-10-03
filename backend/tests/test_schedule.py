"""Study-plan links and due dates."""

from datetime import date

from app.services.llm import _problem_url, _schedule


def test_problem_url_uses_the_leetcode_slug():
    assert (
        _problem_url("Longest Substring Without Repeating Characters", None)
        == "https://leetcode.com/problems/longest-substring-without-repeating-characters/"
    )


def test_due_dates_follow_the_repair_pace():
    plan = _schedule(
        {
            "study_plan": [
                {
                    "topic": "Stack",
                    "problems": [
                        {"title": "Valid Parentheses", "difficulty": "Easy", "url": "https://leetcode.com/problems/valid-parentheses/"},
                        {"title": "Daily Temperatures", "difficulty": "Medium", "url": "https://leetcode.com/problems/daily-temperatures/"},
                    ],
                }
            ]
        },
        "repair",
        today=date(2026, 10, 3),
    )
    problems = plan["study_plan"][0]["problems"]
    assert problems[0]["due"] == "2026-10-05"
    assert problems[1]["due"] == "2026-10-08"
    assert plan["study_plan"][0]["topic_due"] == "2026-10-08"
