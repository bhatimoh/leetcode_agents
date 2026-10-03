"""Agent 2: score the last five contests, decide the focus, then write the plan."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.nodes.finish import build_facts
from app.agents.progress import report
from app.agents.state import TraceStep
from app.services.llm import decide_focus, write_plan


class CoachState(TypedDict, total=False):
    facts: dict
    performance: dict
    decision: dict | None
    user_knowledge: dict | None
    aligned: bool
    replans: int
    revision: str | None
    trace: list[TraceStep]
    error: str | None


def score_contests(recent: list[dict]) -> dict:
    rows = []
    for row in recent:
        solved = int(row.get("problems_solved") or 0)
        total = int(row.get("total_problems") or 0)
        rows.append({"title": row.get("title") or "Contest", "solved": solved, "total": total})

    if not rows:
        return {
            "rows": [],
            "missed": 0,
            "trend": "none",
            "summary": "No attended contests in the public history.",
        }

    missed = sum(max(row["total"] - row["solved"], 0) for row in rows)
    rates = [row["solved"] / row["total"] if row["total"] else 0 for row in rows]
    latest = rates[0]
    older = sum(rates[1:]) / (len(rates) - 1) if len(rates) > 1 else latest
    if len(rates) == 1:
        trend = "single"
    elif latest > older + 0.12:
        trend = "improving"
    elif latest + 0.12 < older:
        trend = "dropping"
    else:
        trend = "steady"

    counts = ", ".join(f"{row['solved']}/{row['total']} in {row['title']}" for row in rows)
    return {
        "rows": rows,
        "missed": missed,
        "trend": trend,
        "summary": f"Previous contests: {counts}. Trend is {trend}. Questions missed: {missed}.",
    }


def _aligned(decision: dict, knowledge: dict) -> bool:
    planned = " ".join(
        f"{step.get('topic', '')} {step.get('focus', '')}" for step in knowledge.get("study_plan") or []
    ).lower()
    summary = str(knowledge.get("summary") or "").lower()
    text = f"{planned} {summary}"
    for topic in decision.get("focus_topics") or []:
        tag = str(topic.get("tag") or "").lower()
        if tag and tag not in text:
            return False
    return bool(decision.get("focus_topics"))


async def assess(state: CoachState) -> dict:
    await report({"type": "status", "agent": 2, "detail": "Scoring questions solved in the previous five contests."})
    performance = score_contests((state.get("facts") or {}).get("recent_contests") or [])
    trace = list(state.get("trace") or [])
    trace.append({"phase": "assess", "detail": performance["summary"]})
    await report({"type": "trace", "agent": 2, "trace": trace})
    return {"performance": performance, "trace": trace}


async def decide(state: CoachState) -> dict:
    await report({"type": "status", "agent": 2, "detail": "Choosing the topics to focus on from that contest performance."})
    trace = list(state.get("trace") or [])
    try:
        decision = await decide_focus(state["facts"], state["performance"])
    except Exception as exc:  # noqa: BLE001 - show the model failure on the run
        trace.append({"phase": "decide", "detail": "The focus decision failed."})
        await report({"type": "trace", "agent": 2, "trace": trace})
        return {"trace": trace, "error": str(exc)}

    tags = ", ".join(topic["tag"] for topic in decision["focus_topics"])
    detail = f"{decision['contest_read']} Focus: {tags}."
    trace.append({"phase": "decide", "detail": detail})
    await report({"type": "trace", "agent": 2, "trace": trace, "decision": decision})
    return {"decision": decision, "trace": trace, "error": None}


async def plan_advice(state: CoachState) -> dict:
    await report({"type": "status", "agent": 2, "detail": "Writing the study plan around the chosen topics."})
    trace = list(state.get("trace") or [])
    if state.get("error"):
        return {}
    try:
        knowledge = await write_plan(
            state["facts"],
            state["performance"],
            state["decision"],
            state.get("revision"),
        )
    except Exception as exc:  # noqa: BLE001
        trace.append({"phase": "plan", "detail": "The study plan failed."})
        await report({"type": "trace", "agent": 2, "trace": trace})
        return {"trace": trace, "error": str(exc)}

    tags = ", ".join(step["topic"] for step in knowledge["study_plan"])
    trace.append({"phase": "plan", "detail": f"Study plan covers {tags}."})
    await report({"type": "trace", "agent": 2, "trace": trace})
    return {"user_knowledge": knowledge, "trace": trace, "error": None}


async def review(state: CoachState) -> dict:
    await report({"type": "status", "agent": 2, "detail": "Checking the plan against the focus decision."})
    trace = list(state.get("trace") or [])
    if state.get("error") or not state.get("decision") or not state.get("user_knowledge"):
        trace.append({"phase": "review", "detail": "Stopped before the plan could be checked."})
        await report({"type": "trace", "agent": 2, "trace": trace})
        return {"aligned": True, "trace": trace}

    if _aligned(state["decision"], state["user_knowledge"]):
        trace.append({"phase": "review", "detail": "The plan matches the focus topics."})
        await report({"type": "trace", "agent": 2, "trace": trace})
        return {"aligned": True, "trace": trace}

    replans = int(state.get("replans") or 0)
    tags = ", ".join(topic["tag"] for topic in state["decision"]["focus_topics"])
    if replans >= 1:
        trace.append({"phase": "review", "detail": f"Keeping the plan. Expected focus was {tags}."})
        await report({"type": "trace", "agent": 2, "trace": trace})
        return {"aligned": True, "trace": trace, "replans": replans}

    trace.append({"phase": "review", "detail": f"The plan missed {tags}. Writing it again."})
    await report({"type": "trace", "agent": 2, "trace": trace})
    return {
        "aligned": False,
        "replans": replans + 1,
        "revision": f"The previous plan did not use these focus topics: {tags}. Rewrite it.",
        "trace": trace,
    }


def _after_decide(state: CoachState) -> str:
    if state.get("error"):
        return "end"
    return "plan"


def _after_review(state: CoachState) -> str:
    if state.get("aligned"):
        return "end"
    return "plan"


def build_coach():
    graph = StateGraph(CoachState)
    graph.add_node("assess", assess)
    graph.add_node("decide", decide)
    graph.add_node("plan", plan_advice)
    graph.add_node("review", review)
    graph.add_edge(START, "assess")
    graph.add_edge("assess", "decide")
    graph.add_conditional_edges("decide", _after_decide, {"plan": "plan", "end": END})
    graph.add_edge("plan", "review")
    graph.add_conditional_edges("review", _after_review, {"plan": "plan", "end": END})
    return graph.compile()


coach = build_coach()


def coach_state(username: str, profile: dict, contest: dict | None, submissions: list[dict] | None) -> CoachState:
    return {
        "facts": build_facts(username, profile, contest, submissions),
        "performance": {},
        "decision": None,
        "user_knowledge": None,
        "aligned": False,
        "replans": 0,
        "revision": None,
        "trace": [],
        "error": None,
    }
