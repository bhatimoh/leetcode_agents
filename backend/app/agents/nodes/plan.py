"""Decide which tools are still missing."""

from app.agents.state import AgentState

TOOL_NAMES = ("profile", "contest", "submissions")
MAX_ATTEMPTS = 2


def pending_tools(state: AgentState) -> list[str]:
    attempts = state.get("attempts") or {}
    pending: list[str] = []
    for name in TOOL_NAMES:
        if state.get(name) is None and attempts.get(name, 0) < MAX_ATTEMPTS:
            pending.append(name)
    return pending


def knows_enough(state: AgentState) -> bool:
    return len(pending_tools(state)) == 0
