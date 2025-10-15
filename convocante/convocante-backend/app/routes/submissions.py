# app/routes/submissions.py
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timezone
from ..config import settings
import os

router = APIRouter(prefix="/api", tags=["submissions"])

ALLOWED_FILES = {
    "content.zip": "application/zip",
    "manifest.json": "application/json",
    "signature.bin": "application/octet-stream",
    "sealed_base.zip": "application/zip",
    "result.json": "application/json",
}

def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")

@router.get("/calls/{call_id}/submissions")
def list_submissions(call_id: str):
    base = settings.PROCESSED_DIR / call_id
    if not base.exists():
        return []  # sin submissions todavía

    items = []
    # Directorios con timestamps (yyyyMMdd-HHmmss)
    for entry in base.iterdir():
        if not entry.is_dir():
            continue
        # metadatos de carpeta
        st = entry.stat()
        submission_id = entry.name
        created_at = _iso(st.st_mtime)

        files = []
        for fname, mime in ALLOWED_FILES.items():
            fpath = entry / fname
            if fpath.exists():
                fstat = fpath.stat()
                files.append({
                    "name": fname,
                    "size": fstat.st_size,
                    "modified_at": _iso(fstat.st_mtime),
                    "download_url": f"/convocante/api/calls/{call_id}/submissions/{submission_id}/files/{fname}",
                })

        items.append({
            "submission_id": submission_id,
            "created_at": created_at,
            "files": files,
        })

    # Orden descendente por submission_id (timestamp en el nombre)
    items.sort(key=lambda x: x["submission_id"], reverse=True)
    return items

@router.get("/calls/{call_id}/submissions/{submission_id}/files/{filename}")
def download_submission_file(call_id: str, submission_id: str, filename: str):
    if filename not in ALLOWED_FILES:
        raise HTTPException(status_code=400, detail="filename not allowed")

    base = settings.PROCESSED_DIR / call_id / submission_id
    fpath = (base / filename).resolve()

    # evitar path traversal y verificar existencia
    if not str(fpath).startswith(str((settings.PROCESSED_DIR / call_id).resolve())):
        raise HTTPException(status_code=400, detail="invalid path")
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="file not found")

    media_type = ALLOWED_FILES[filename]
    # Para JSON, si prefieres inline en vez de descarga, podrías leer y devolver Response(text, media_type).
    return FileResponse(path=fpath, media_type=media_type, filename=filename)
