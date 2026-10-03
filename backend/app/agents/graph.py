"""LangGraph loop: plan, act, observe, then finish."""

from langgraph.graph import END, START, StateGraph

from app.agents.nodes.act import act
from app.agents.nodes.observe import observe
from app.agents.nodes.plan import pending_tools
from app.agents.progress import report
from app.agents.state import AgentState


async def plan(state: AgentState) -> dict:
    await report({"type": "status", "agent": 1, "detail": "Deciding which records are still missing."})
    pending = pending_tools(state)
    trace = list(state.get("trace") or [])
    if pending:
        detail = "Need " + ", ".join(pending) + "."
    elif state.get("profile") is None:
        detail = "No profile loaded. Finish with what we have."
    else:
        detail = "No more tools to call."
    trace.append({"phase": "plan", "detail": detail})
    await report({"type": "trace", "agent": 1, "trace": trace})
    return {"pending": pending, "enough": not pending, "trace": trace}


async def finish(state: AgentState) -> dict:
    trace = list(state.get("trace") or [])
    if state.get("profile") is None:
        detail = f"No public LeetCode profile for {state.get('username', 'that user')}."
        trace.append({"phase": "finish", "detail": detail})
        await report({"type": "trace", "agent": 1, "trace": trace})
        await report({"type": "status", "agent": 1, "detail": detail})
        return {"trace": trace, "error": detail}

    trace.append({"phase": "finish", "detail": "Records are ready for the coach."})
    await report({"type": "trace", "agent": 1, "trace": trace})
    await report({"type": "status", "agent": 1, "detail": "Records are ready for the coach."})
    return {"trace": trace, "error": None}


def _after_plan(state: AgentState) -> str:
    if state.get("enough"):
        return "finish"
    return "act"


def _after_observe(state: AgentState) -> str:
    if state.get("enough"):
        return "finish"
    return "plan"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan)
    graph.add_node("act", act)
    graph.add_node("observe", observe)
    graph.add_node("finish", finish)
    graph.add_edge(START, "plan")
    graph.add_conditional_edges("plan", _after_plan, {"act": "act", "finish": "finish"})
    graph.add_edge("act", "observe")
    graph.add_conditional_edges("observe", _after_observe, {"plan": "plan", "finish": "finish"})
    graph.add_edge("finish", END)
    return graph.compile()


agent = build_graph()


def initial_state(username: str) -> AgentState:
    return {
        "username": username,
        "profile": None,
        "contest": None,
        "submissions": None,
        "attempts": {},
        "pending": [],
        "enough": False,
        "trace": [],
        "user_knowledge": None,
        "error": None,
    }
