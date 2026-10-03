"""Start one agent run for a LeetCode username."""

import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.coach import coach, coach_state
from app.agents.graph import agent, initial_state
from app.agents.progress import reset_emitter, set_emitter
from app.schemas.analysis import AnalysisRequest, present

router = APIRouter()


def _fail(result: dict) -> HTTPException | None:
    if not result.get("error"):
        return None
    missing_profile = str(result["error"]).startswith("No public LeetCode profile")
    status = 404 if missing_profile else 502
    return HTTPException(status_code=status, detail=result["error"])


@router.post("/analysis")
async def run_analysis(body: AnalysisRequest):
    username = body.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Username is required.")
    gathered = await agent.ainvoke(initial_state(username))
    failure = _fail(gathered)
    if failure:
        raise failure
    advised = await coach.ainvoke(
        coach_state(username, gathered["profile"], gathered.get("contest"), gathered.get("submissions"))
    )
    failure = _fail(advised)
    if failure:
        raise failure
    gathered["user_knowledge"] = advised.get("user_knowledge")
    gathered["trace"] = list(gathered.get("trace") or []) + list(advised.get("trace") or [])
    return present(gathered)


@router.post("/analysis/stream")
async def stream_analysis(body: AnalysisRequest):
    username = body.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Username is required.")

    async def generate():
        queue: asyncio.Queue = asyncio.Queue()

        async def emit(event: dict) -> None:
            await queue.put(event)

        async def run() -> None:
            token = set_emitter(emit)
            try:
                gathered = await agent.ainvoke(initial_state(username))
                if gathered.get("error"):
                    await queue.put({"type": "error", "detail": gathered["error"]})
                    return
                view = present(gathered)
                await queue.put(
                    {
                        "type": "agent1",
                        "trace": view["trace"],
                        "profile": view["profile"],
                        "contest": view["contest"],
                        "submissions": view["submissions"],
                    }
                )
                advised = await coach.ainvoke(
                    coach_state(username, gathered["profile"], gathered.get("contest"), gathered.get("submissions"))
                )
                if advised.get("error"):
                    await queue.put({"type": "error", "detail": advised["error"]})
                    return
                knowledge = present({"user_knowledge": advised.get("user_knowledge")})["userKnowledge"]
                await queue.put(
                    {
                        "type": "agent2",
                        "trace": advised.get("trace") or [],
                        "decision": advised.get("decision"),
                        "userKnowledge": knowledge,
                    }
                )
            except Exception as exc:  # noqa: BLE001 - keep the stream informed
                await queue.put({"type": "error", "detail": str(exc)})
            finally:
                reset_emitter(token)
                await queue.put(None)

        task = asyncio.create_task(run())
        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"
        await task

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
