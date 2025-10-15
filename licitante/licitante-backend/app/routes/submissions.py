from fastapi import APIRouter
from pathlib import Path
from ..config import settings
from ..storage import read_json

router = APIRouter(prefix="/api", tags=["submissions"])

@router.get("/submissions")
def list_submissions(call_id: str | None = None):
    base = settings.SUBMISSIONS_DIR
    out = []
    if call_id:
        base = base / call_id
    if not base.exists():
        return out
    for call_dir in ([base] if call_id else base.iterdir()):
        if not call_dir.exists() or (not call_dir.is_dir()):
            continue
        for subdir in call_dir.iterdir():
            rec = read_json(subdir / "record.json", None)
            if rec:
                out.append(rec)
    out.sort(key=lambda x: x["id"], reverse=True)
    return out