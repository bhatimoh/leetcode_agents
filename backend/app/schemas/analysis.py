"""Request and response models for an analysis run."""

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    username: str = Field(min_length=1, max_length=40)


def present(result: dict) -> dict:
    profile = result.get("profile") or {}
    contest = result.get("contest") or {
        "attended": 0,
        "rating": None,
        "global_ranking": None,
        "top_percentage": None,
    }
    knowledge = result.get("user_knowledge") or {}
    return {
        "trace": result.get("trace") or [],
        "profile": {
            "username": profile.get("username"),
            "realName": profile.get("real_name"),
            "ranking": profile.get("ranking"),
            "acceptanceRate": profile.get("acceptance_rate") or 0,
            "solved": profile.get("solved") or {"easy": 0, "medium": 0, "hard": 0},
            "tagStats": profile.get("tag_stats") or [],
        },
        "contest": {
            "attended": contest.get("attended") or 0,
            "rating": contest.get("rating"),
            "globalRanking": contest.get("global_ranking"),
            "topPercentage": contest.get("top_percentage"),
            "recent": [
                {
                    "title": row["title"],
                    "problemsSolved": row["problems_solved"],
                    "totalProblems": row["total_problems"],
                }
                for row in contest.get("recent") or []
            ],
        },
        "submissions": [
            {
                "title": row["title"],
                "status": row["status"],
                "language": row["language"],
            }
            for row in (result.get("submissions") or [])
        ],
        "userKnowledge": {
            "summary": knowledge.get("summary", ""),
            "topicGaps": [
                {
                    "tag": gap["tag"],
                    "solved": gap["solved"],
                    "severity": gap["severity"],
                    "howToStudy": gap["how_to_study"],
                }
                for gap in knowledge.get("topic_gaps") or []
            ],
            "stuckLoops": [
                {
                    "title": loop["title"],
                    "tag": loop["tag"],
                    "attempts": loop["attempts"],
                    "lastStatus": loop["last_status"],
                    "note": loop["note"],
                }
                for loop in knowledge.get("stuck_loops") or []
            ],
            "recommendations": knowledge.get("recommendations") or [],
            "studyPlan": [
                {
                    "order": step.get("order"),
                    "topic": step.get("topic"),
                    "focus": step.get("focus"),
                    "topicDue": step.get("topic_due"),
                    "problems": step.get("problems") or [],
                }
                for step in knowledge.get("study_plan") or []
            ],
        },
    }
