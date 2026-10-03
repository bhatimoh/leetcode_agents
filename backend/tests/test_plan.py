"""The planner stops once every tool has a result or two failures."""

from app.agents.nodes.plan import knows_enough, pending_tools


def test_first_plan_asks_for_every_tool():
    state = {"profile": None, "contest": None, "submissions": None, "attempts": {}}
    assert pending_tools(state) == ["profile", "contest", "submissions"]
    assert knows_enough(state) is False


def test_loaded_tools_are_enough():
    state = {
        "profile": {"username": "lee"},
        "contest": {"attended": 0},
        "submissions": [],
        "attempts": {"profile": 1, "contest": 1, "submissions": 1},
    }
    assert pending_tools(state) == []
    assert knows_enough(state) is True


def test_failed_tool_is_retried_once_then_dropped():
    once = {"profile": {"username": "lee"}, "contest": None, "submissions": [], "attempts": {"contest": 1}}
    assert pending_tools(once) == ["contest"]

    twice = {"profile": {"username": "lee"}, "contest": None, "submissions": [], "attempts": {"contest": 2}}
    assert pending_tools(twice) == []
    assert knows_enough(twice) is True
