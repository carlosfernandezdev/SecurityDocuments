from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from datetime import datetime, timezone
from ..config import settings
import mimetypes

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

def _safe_resolve(base: Path, *parts: str) -> Path:
    p = (base.joinpath(*parts)).resolve()
    if not str(p).startswith(str(base.resolve())):
        raise HTTPException(status_code=400, detail="invalid path")
    return p

@router.get("/calls/{call_id}/submissions")
def list_submissions(call_id: str):
    base = settings.PROCESSED_DIR / call_id
    if not base.exists():
        return []
    items = []
    for entry in base.iterdir():
        if not entry.is_dir():
            continue
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

        # contar archivos dentro de content/
        content_dir = entry / "content"
        content_count = 0
        if content_dir.exists():
            content_count = sum(1 for _ in content_dir.rglob("*") if _.is_file())

        items.append({
            "submission_id": submission_id,
            "created_at": created_at,
            "files": files,
            "content": {
                "count": content_count,
                "list_url": f"/convocante/api/calls/{call_id}/submissions/{submission_id}/content"
            }
        })

    items.sort(key=lambda x: x["submission_id"], reverse=True)
    return items

@router.get("/calls/{call_id}/submissions/{submission_id}/files/{filename}")
def download_submission_file(call_id: str, submission_id: str, filename: str):
    if filename not in ALLOWED_FILES:
        raise HTTPException(status_code=400, detail="filename not allowed")

    base = settings.PROCESSED_DIR / call_id / submission_id
    fpath = _safe_resolve(base, filename)
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="file not found")

    media_type = ALLOWED_FILES[filename]
    return FileResponse(path=fpath, media_type=media_type, filename=filename)

# --- Contenido descomprimido ---

@router.get("/calls/{call_id}/submissions/{submission_id}/content")
def list_content_files(call_id: str, submission_id: str):
    content_dir = settings.PROCESSED_DIR / call_id / submission_id / "content"
    if not content_dir.exists():
        return []
    items = []
    for p in content_dir.rglob("*"):
        if p.is_file():
            rel = p.relative_to(content_dir).as_posix()
            st = p.stat()
            items.append({
                "path": rel,
                "size": st.st_size,
                "modified_at": _iso(st.st_mtime),
                "download_url": f"/convocante/api/calls/{call_id}/submissions/{submission_id}/content/{rel}"
            })
    items.sort(key=lambda x: x["path"])
    return items

@router.get("/calls/{call_id}/submissions/{submission_id}/content/{file_path:path}")
def download_content_file(call_id: str, submission_id: str, file_path: str):
    content_dir = settings.PROCESSED_DIR / call_id / submission_id / "content"
    fpath = _safe_resolve(content_dir, file_path)
    if not fpath.exists() or not fpath.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    guess, _ = mimetypes.guess_type(fpath.name)
    media_type = guess or "application/octet-stream"
    return FileResponse(path=fpath, media_type=media_type, filename=fpath.name)
