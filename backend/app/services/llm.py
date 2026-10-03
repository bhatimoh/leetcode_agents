"""OpenAI chat call that turns contest facts into a study plan."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta

import httpx

from app.core.config import settings

SYSTEM_PROMPT = """You are a LeetCode coach writing the final plan after a decision has already been made.
Follow the focus topics in the decision. The study_plan topics must be those focus topics, in the same order.
Use the contest scores exactly as given. Do not change them.
Return one JSON object and nothing else, with these keys:
summary: string. State the contest solve counts, the trend, and why the focus topics were chosen.
topic_gaps: array of {tag, solved, severity, how_to_study}. severity is "high" or "medium". Tags come from the decision.
stuck_loops: array of {title, tag, attempts, last_status, note}. Include only problems named in the facts. If none, return [].
recommendations: array of 4 {title, difficulty, tag, reason}. difficulty is "Easy", "Medium", or "Hard". title must be a real LeetCode problem. Tie each reason to the contest performance.
study_plan: array of {order, topic, focus, problems}. One step per focus topic. order starts at 1.
Each problem is {title, slug, difficulty}. slug is the real LeetCode title slug, lowercase words joined by hyphens, as used in https://leetcode.com/problems/<slug>/. difficulty is Easy, Medium, or Hard.
recommendations also include slug for each problem.
"""

DECIDE_PROMPT = """You decide what this person should practice next. The previous five contests are the main evidence.
Look at questions solved out of questions offered, the trend, and the thinnest topics.
Return one JSON object:
contest_read: one or two sentences naming the contests and the solved/total counts.
pace: "repair" when a question is missed in most contests, "stretch" when nearly every question is solved, "rebuild" when there are no contests.
focus_topics: 2 or 3 items of {tag, why}. Prefer tags from thinnest_topics. The why must mention the contest scores.
"""


async def _chat(system: str, user: dict) -> dict:
    if not settings.openai_api_key:
        raise RuntimeError("Set OPENAI_API_KEY in backend/.env. The agent calls OpenAI to write the plan.")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.openai_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openai_model,
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(user)},
                ],
            },
        )
    if response.status_code >= 400:
        detail = response.text[:300]
        raise RuntimeError(f"OpenAI request failed ({response.status_code}). {detail}")
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


async def decide_focus(facts: dict, performance: dict) -> dict:
    payload = await _chat(DECIDE_PROMPT, {"facts": facts, "performance": performance})
    topics = []
    for topic in payload.get("focus_topics") or []:
        tag = str(topic.get("tag") or "").strip()
        if not tag:
            continue
        topics.append({"tag": tag, "why": str(topic.get("why") or "")})
    if len(topics) < 2:
        raise RuntimeError("The model did not choose focus topics from the contest scores.")
    pace = payload.get("pace") if payload.get("pace") in {"repair", "stretch", "rebuild"} else "repair"
    return {
        "contest_read": str(payload.get("contest_read") or performance.get("summary") or ""),
        "pace": pace,
        "focus_topics": topics[:3],
    }


async def write_plan(facts: dict, performance: dict, decision: dict, revision: str | None = None) -> dict:
    payload = await _chat(
        SYSTEM_PROMPT,
        {
            "facts": facts,
            "performance": performance,
            "decision": decision,
            "revision": revision,
        },
    )
    return _schedule(_normalize(payload), str(decision.get("pace") or "repair"))


def _normalize(payload: dict) -> dict:
    gaps = []
    for gap in payload.get("topic_gaps") or []:
        severity = gap.get("severity") if gap.get("severity") in {"high", "medium"} else "medium"
        gaps.append(
            {
                "tag": str(gap.get("tag") or "Practice"),
                "solved": int(gap.get("solved") or 0),
                "severity": severity,
                "how_to_study": str(gap.get("how_to_study") or ""),
            }
        )

    loops = []
    for loop in payload.get("stuck_loops") or []:
        loops.append(
            {
                "title": str(loop.get("title") or "Problem"),
                "tag": str(loop.get("tag") or "Recent submissions"),
                "attempts": int(loop.get("attempts") or 0),
                "last_status": str(loop.get("last_status") or "Unknown"),
                "note": str(loop.get("note") or ""),
            }
        )

    recommendations = []
    for item in payload.get("recommendations") or []:
        difficulty = item.get("difficulty") if item.get("difficulty") in {"Easy", "Medium", "Hard"} else "Medium"
        recommendations.append(
            {
                "title": str(item.get("title") or "Practice problem"),
                "difficulty": difficulty,
                "tag": str(item.get("tag") or ""),
                "reason": str(item.get("reason") or ""),
                "url": _problem_url(str(item.get("title") or ""), item.get("slug")),
            }
        )

    steps = []
    for index, step in enumerate(payload.get("study_plan") or [], start=1):
        problems = []
        for problem in step.get("problems") or []:
            if isinstance(problem, str):
                title = problem
                slug = None
                difficulty = "Medium"
            else:
                title = str(problem.get("title") or "Practice problem")
                slug = problem.get("slug")
                difficulty = problem.get("difficulty") if problem.get("difficulty") in {"Easy", "Medium", "Hard"} else "Medium"
            problems.append(
                {
                    "title": title,
                    "difficulty": difficulty,
                    "url": _problem_url(title, slug),
                }
            )
        steps.append(
            {
                "order": int(step.get("order") or index),
                "topic": str(step.get("topic") or "Practice"),
                "focus": str(step.get("focus") or ""),
                "problems": problems,
            }
        )

    if not payload.get("summary") or not steps:
        raise RuntimeError("The model response did not include a summary and a study plan.")

    return {
        "summary": str(payload["summary"]),
        "topic_gaps": gaps,
        "stuck_loops": loops,
        "recommendations": recommendations,
        "study_plan": steps,
    }


def _problem_url(title: str, slug: str | None) -> str:
    raw = (slug or title).lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return f"https://leetcode.com/problems/{cleaned}/"


_PACE_DAYS = {
    "rebuild": {"Easy": 1, "Medium": 2, "Hard": 3},
    "repair": {"Easy": 2, "Medium": 3, "Hard": 4},
    "stretch": {"Easy": 2, "Medium": 4, "Hard": 6},
}


def _schedule(plan: dict, pace: str, today: date | None = None) -> dict:
    """Give each weak-topic problem a due date, spaced by difficulty and pace."""
    start = today or date.today()
    gaps = _PACE_DAYS.get(pace, _PACE_DAYS["repair"])
    cursor = start
    for step in plan["study_plan"]:
        for problem in step["problems"]:
            cursor = cursor + timedelta(days=gaps[problem["difficulty"]])
            problem["due"] = cursor.isoformat()
        if step["problems"]:
            step["topic_due"] = step["problems"][-1]["due"]
        else:
            step["topic_due"] = start.isoformat()
    return plan
