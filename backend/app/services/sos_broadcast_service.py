from sqlalchemy.ext.asyncio import AsyncSession

from app.core.websocket_manager import CAPTAINS_GROUP, connection_manager
from app.models.misc import SosAlert
from app.schemas.missions_4_5_6 import SosAlertOut


async def trigger_sos(db: AsyncSession, location: str) -> SosAlert:
    alert = SosAlert(location=location)
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    # Broadcast happens after commit so a captain who reconnects and re-fetches
    # history always sees an alert that's actually persisted, never a "ghost"
    # alert that only existed on the wire.
    await connection_manager.broadcast(
        CAPTAINS_GROUP,
        {"event": "sos_triggered", "alert": SosAlertOut.model_validate(alert).model_dump(mode="json")},
    )
    return alert
