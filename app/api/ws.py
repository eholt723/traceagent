import asyncio
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])

# run_id → asyncio.Queue of {"event": str|None, "data": Any}
run_queues: dict[int, asyncio.Queue] = {}


async def emit(run_id: int, event: str | None, data: Any) -> None:
    queue = run_queues.get(run_id)
    if queue:
        await queue.put({"event": event, "data": data})


@router.websocket("/ws/runs/{run_id}")
async def ws_run(websocket: WebSocket, run_id: int):
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue()
    run_queues[run_id] = queue
    try:
        while True:
            msg = await queue.get()
            if msg["event"] is None:  # sentinel from pipeline
                break
            await websocket.send_json(msg)
    except WebSocketDisconnect:
        pass
    finally:
        run_queues.pop(run_id, None)
        await websocket.close()
