"""Call the tools the planner selected."""

import asyncio

from app.agents.progress import report
from app.agents.state import AgentState
from app.services.leetcode_client import fetch_contest, fetch_profile, fetch_submissions

TOOLS = {
    "profile": fetch_profile,
    "contest": fetch_contest,
    "submissions": fetch_submissions,
}


async def act(state: AgentState) -> dict:
    pending = list(state.get("pending") or [])
    names = ", ".join(pending) if pending else "no tools"
    await report({"type": "status", "agent": 1, "detail": f"Fetching {names}."})
    attempts = dict(state.get("attempts") or {})
    updates: dict = {"attempts": attempts}
    errors: list[str] = []

    async def run(name: str):
        try:
            value = await TOOLS[name](state["username"])
            return name, value, None
        except Exception as exc:  # noqa: BLE001 - tool failures are observations
            return name, None, str(exc)

    results = await asyncio.gather(*(run(name) for name in pending))
    for name, value, error in results:
        attempts[name] = attempts.get(name, 0) + 1
        if error:
            errors.append(f"{name} failed: {error}")
        else:
            updates[name] = value

    detail = "Called " + ", ".join(pending) + "."
    if errors:
        detail = f"{detail} {' '.join(errors)}"
    trace = list(state.get("trace") or [])
    trace.append({"phase": "act", "detail": detail})
    updates["trace"] = trace
    updates["attempts"] = attempts
    await report({"type": "trace", "agent": 1, "trace": trace})
    return updates
