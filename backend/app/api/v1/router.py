from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    complaints,
    dashboard,
    factcheck,
    ledger,
    oauth,
    seating,
    sos,
    syllabus,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(oauth.router)
api_router.include_router(dashboard.router)
api_router.include_router(complaints.router)
api_router.include_router(seating.router)
api_router.include_router(syllabus.router)
api_router.include_router(ledger.router)
api_router.include_router(sos.router)
api_router.include_router(factcheck.router)
