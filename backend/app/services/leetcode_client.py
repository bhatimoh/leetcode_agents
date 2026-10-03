"""Public LeetCode GraphQL calls used as agent tools."""

from __future__ import annotations

import httpx

from app.core.config import settings

PROFILE_QUERY = """
query ($username: String!) {
  matchedUser(username: $username) {
    username
    profile { realName ranking }
    submitStats {
      acSubmissionNum { difficulty count submissions }
      totalSubmissionNum { difficulty count submissions }
    }
    tagProblemCounts {
      fundamental { tagName problemsSolved }
      intermediate { tagName problemsSolved }
      advanced { tagName problemsSolved }
    }
  }
}
"""

CONTEST_QUERY = """
query ($username: String!) {
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    topPercentage
  }
  userContestRankingHistory(username: $username) {
    attended
    problemsSolved
    totalProblems
    contest { title }
  }
}
"""

SUBMISSION_QUERY = """
query ($username: String!, $limit: Int!) {
  recentSubmissionList(username: $username, limit: $limit) {
    title
    statusDisplay
    lang
  }
}
"""


async def graphql(query: str, variables: dict) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            settings.leetcode_graphql_url,
            json={"query": query, "variables": variables},
            headers={
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com",
                "User-Agent": "leetcode-analytics",
            },
        )
        response.raise_for_status()
        payload = response.json()
    errors = payload.get("errors") or []
    if errors:
        message = errors[0].get("message") or "LeetCode query failed"
        raise RuntimeError(message)
    return payload["data"]


def _count(rows: list[dict], difficulty: str, field: str) -> int:
    for row in rows:
        if row.get("difficulty") == difficulty:
            return int(row.get(field) or 0)
    return 0


async def fetch_profile(username: str) -> dict:
    data = await graphql(PROFILE_QUERY, {"username": username})
    user = data.get("matchedUser")
    if not user:
        raise LookupError(f"No public profile for {username}")

    profile = user.get("profile") or {}
    stats = user.get("submitStats") or {}
    accepted = stats.get("acSubmissionNum") or []
    totals = stats.get("totalSubmissionNum") or []
    accepted_submissions = _count(accepted, "All", "submissions")
    total_submissions = _count(totals, "All", "submissions")
    acceptance = 0.0 if total_submissions == 0 else (accepted_submissions / total_submissions) * 100

    tags: list[dict] = []
    grouped = user.get("tagProblemCounts") or {}
    for level in ("fundamental", "intermediate", "advanced"):
        for tag in grouped.get(level) or []:
            tags.append({"tag": tag["tagName"], "solved": int(tag.get("problemsSolved") or 0)})
    tags.sort(key=lambda item: item["solved"], reverse=True)

    return {
        "username": user["username"],
        "real_name": profile.get("realName") or user["username"],
        "ranking": profile.get("ranking"),
        "acceptance_rate": round(acceptance, 1),
        "solved": {
            "easy": _count(accepted, "Easy", "count"),
            "medium": _count(accepted, "Medium", "count"),
            "hard": _count(accepted, "Hard", "count"),
        },
        "tag_stats": tags[:12],
        "all_tags": tags,
    }


def _recent_contests(history: list[dict]) -> list[dict]:
    attended = [row for row in history if row.get("attended")]
    recent = []
    for row in attended[-5:]:
        contest = row.get("contest") or {}
        recent.append(
            {
                "title": contest.get("title") or "Contest",
                "problems_solved": int(row.get("problemsSolved") or 0),
                "total_problems": int(row.get("totalProblems") or 0),
            }
        )
    recent.reverse()
    return recent


async def fetch_contest(username: str) -> dict:
    data = await graphql(CONTEST_QUERY, {"username": username})
    ranking = data.get("userContestRanking") or {}
    return {
        "attended": int(ranking.get("attendedContestsCount") or 0),
        "rating": ranking.get("rating"),
        "global_ranking": ranking.get("globalRanking"),
        "top_percentage": ranking.get("topPercentage"),
        "recent": _recent_contests(data.get("userContestRankingHistory") or []),
    }


async def fetch_submissions(username: str) -> list[dict]:
    data = await graphql(SUBMISSION_QUERY, {"username": username, "limit": 20})
    rows = data.get("recentSubmissionList") or []
    return [
        {
            "title": row.get("title") or "Untitled",
            "status": row.get("statusDisplay") or "Unknown",
            "language": row.get("lang") or "",
        }
        for row in rows
    ]
