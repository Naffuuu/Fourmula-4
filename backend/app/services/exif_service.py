"""Strips EXIF metadata (GPS coordinates, device serial/model, timestamps)
from uploaded evidence photos before they ever touch persistent storage.
Without this, a "GPS: dorm room 4B" tag embedded by the phone's camera app
could re-identify an anonymous whistleblower more precisely than anything
else in the pipeline."""

import io
import uuid
from pathlib import Path

import piexif
from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.config import get_settings

settings = get_settings()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB


async def strip_exif_and_store(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, or WEBP evidence images are accepted.",
        )

    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image too large (max 8MB).")

    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except Exception as exc:  # noqa: BLE001 - any decode failure is a bad upload, not a server error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read image file.") from exc

    # Rebuilding the image from decoded pixel data (rather than just deleting
    # the EXIF APP1 segment from the original bytes) guarantees no metadata
    # survives, including vendor-specific maker notes piexif doesn't parse.
    clean_buffer = io.BytesIO()
    save_format = "JPEG" if file.content_type == "image/jpeg" else image.format or "PNG"
    if save_format == "JPEG" and image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(clean_buffer, format=save_format)
    clean_buffer.seek(0)

    # Belt-and-suspenders: also explicitly strip via piexif for JPEGs, in case
    # a future format-preserving optimization reintroduces an EXIF segment.
    if save_format == "JPEG":
        try:
            scrubbed_bytes = piexif.remove(clean_buffer.getvalue())
            clean_buffer = io.BytesIO(scrubbed_bytes)
        except Exception:  # noqa: BLE001 - piexif raises if there's no EXIF to remove, which is fine
            pass

    uploads_dir = Path(settings.uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.{'jpg' if save_format == 'JPEG' else save_format.lower()}"
    dest_path = uploads_dir / filename
    dest_path.write_bytes(clean_buffer.getvalue())

    # In prod this returns an S3-style URL instead; see storage abstraction
    # note in README "What's deferred".
    return f"/uploads/{filename}"
