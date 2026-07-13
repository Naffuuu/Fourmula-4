from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import decode_access_token
from app.core.websocket_manager import CAPTAINS_GROUP, connection_manager
from app.db.session import AsyncSessionLocal, get_db
from app.models.misc import SosAlert
from app.models.user import User
from app.schemas.missions_4_5_6 import SosAlertCreate, SosAlertOut
from app.services.sos_broadcast_service import trigger_sos

router = APIRouter(prefix="/sos", tags=["sos"])


@router.post("", response_model=SosAlertOut, status_code=201)
async def send_sos(
    payload: SosAlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Persists the alert, then broadcasts it to every connected captain
    socket in the same request — see sos_broadcast_service.py. The <500ms
    target in the brief is about this broadcast fan-out, not the HTTP
    round-trip itself."""
    alert = await trigger_sos(db, payload.location)
    return SosAlertOut.model_validate(alert)


@router.get("", response_model=list[SosAlertOut])
async def list_sos_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returned to any authenticated user on connect/reconnect so the
    IndexedDB-backed offline queue on the frontend has something to
    reconcile against — not just relying on the live socket feed."""
    result = await db.execute(select(SosAlert).order_by(SosAlert.triggered_at.desc()).limit(50))
    return [SosAlertOut.model_validate(a) for a in result.scalars().all()]


@router.websocket("/ws")
async def sos_websocket(websocket: WebSocket, token: str = Query(default="")):
    """Captains' live feed. Auth is via a `?token=` query param (browsers
    can't set custom headers on the WebSocket handshake) carrying the same
    short-lived access token used for REST calls; a stolen link is no worse
    than a stolen access token already is, and it expires in minutes."""
    try:
        payload = decode_access_token(token)
    except ValueError:
        await websocket.close(code=4401)
        return

    async with AsyncSessionLocal() as db:
        user = await db.get(User, payload.get("sub"))
        if not user or user.role.value not in ("second_captain", "third_captain"):
            await websocket.close(code=4403)
            return

    await connection_manager.connect(CAPTAINS_GROUP, websocket)
    try:
        while True:
            # Captains' clients don't need to send anything up this socket
            # today, but we keep the receive loop alive to detect disconnects
            # promptly rather than relying solely on TCP timeouts.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect(CAPTAINS_GROUP, websocket)
