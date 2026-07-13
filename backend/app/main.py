from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.limiter import limiter

settings = get_settings()

app = FastAPI(
    title="Anti-Kuddus Protocol API",
    version="0.1.0",
    description="Backend for the Anti-Kuddus Protocol student accountability platform.",
)

app.state.limiter = limiter

# CORS: explicit origin allowlist, never "*", since auth uses credentialed
# (cookie) requests — a wildcard origin with credentials is rejected by
# browsers anyway, but we also don't want to accidentally allow it server-side.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many attempts. Please wait a moment and try again."},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Consistent error schema across the API: {"detail": ...} always, so the
    frontend's toast/error-state handling doesn't need special cases per
    endpoint. Never leaks a raw Python stack trace to the client."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.get("/health", tags=["meta"])
async def health_check():
    return {"status": "ok"}


uploads_path = Path(settings.uploads_dir)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

app.include_router(api_router, prefix="/api/v1")
