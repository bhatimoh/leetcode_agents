"""Look at tool results and decide whether to re-plan."""

from app.agents.nodes.plan import knows_enough, pending_tools
from app.agents.progress import report
from app.agents.state import AgentState


async def observe(state: AgentState) -> dict:
    await report({"type": "status", "agent": 1, "detail": "Checking whether the profile, contests, and submissions are enough."})
    trace = list(state.get("trace") or [])
    if knows_enough(state):
        if state.get("profile") is None:
            detail = "Profile never loaded. Stopping instead of calling tools again."
        else:
            missing = [name for name in ("profile", "contest", "submissions") if state.get(name) is None]
            if missing:
                detail = "Stopping after retries. Still missing " + ", ".join(missing) + "."
            else:
                detail = "Profile, contest, and submissions are in the state. Enough to finish."
        trace.append({"phase": "observe", "detail": detail})
        await report({"type": "trace", "agent": 1, "trace": trace})
        return {"enough": True, "trace": trace}

    missing = ", ".join(pending_tools(state))
    trace.append({"phase": "observe", "detail": f"Still missing {missing}. Re-planning."})
    await report({"type": "trace", "agent": 1, "trace": trace})
    return {"enough": False, "trace": trace}
