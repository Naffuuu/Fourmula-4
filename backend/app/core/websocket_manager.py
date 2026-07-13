import asyncio
import json

from fastapi import WebSocket


class ConnectionManager:
    """Tracks active WebSocket connections keyed by user_id and role, so an
    SOS alert can be broadcast to every currently-connected captain in
    well under 500ms (in-process pub/sub — no message broker needed at
    hackathon scale; swapping in Redis pub/sub for multi-instance deploys is
    a drop-in change behind this same interface)."""

    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, group: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(group, set()).add(websocket)

    async def disconnect(self, group: str, websocket: WebSocket):
        async with self._lock:
            self._connections.get(group, set()).discard(websocket)

    async def broadcast(self, group: str, message: dict):
        payload = json.dumps(message)
        dead: list[WebSocket] = []
        for ws in list(self._connections.get(group, set())):
            try:
                await ws.send_text(payload)
            except Exception:  # noqa: BLE001 - a dead socket shouldn't break the broadcast to everyone else
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self._connections.get(group, set()).discard(ws)


# One manager per process. The "captains" group receives every SOS alert;
# each mission could get its own group as the app grows.
connection_manager = ConnectionManager()
CAPTAINS_GROUP = "captains"
