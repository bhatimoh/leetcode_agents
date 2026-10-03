"""Live status events from a running agent graph."""

import contextvars
from collections.abc import Awaitable, Callable

Emitter = Callable[[dict], Awaitable[None]]

_emitter: contextvars.ContextVar[Emitter | None] = contextvars.ContextVar("agent_emitter", default=None)


def set_emitter(emitter: Emitter | None):
    return _emitter.set(emitter)


def reset_emitter(token) -> None:
    _emitter.reset(token)


async def report(event: dict) -> None:
    emitter = _emitter.get()
    if emitter is not None:
        await emitter(event)
