"""Shared state for one analytics run."""

from typing import TypedDict


class TraceStep(TypedDict):
    phase: str
    detail: str


class AgentState(TypedDict, total=False):
    username: str
    profile: dict | None
    contest: dict | None
    submissions: list[dict] | None
    attempts: dict[str, int]
    pending: list[str]
    enough: bool
    trace: list[TraceStep]
    user_knowledge: dict | None
    error: str | None
