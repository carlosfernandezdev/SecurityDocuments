# app.py — LICITANTE (versión corregida y completa)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, Form, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Set, List, Any
from datetime import datetime
from pathlib import Path
import uuid
import os
import json
import io
import zipfile
import httpx
import tempfile
import shutil

# =========================
# Config & Storage
# =========================
CONVOCANTE_URL = os.getenv(
    "CONVOCANTE_URL",
    "http://127.0.0.1:8001/convocante/internal/receive-proposal?secret=SHARED_SECRET",
)

LICITANTE_SECRET = "UN_SECRETO_COMPARTIDO"  # para validar webhook del convocante
DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

CALLS_DB = DATA_DIR / "calls.json"
SUBS_DB = DATA_DIR / "submissions.json"

def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception:
        return default

def _atomic_write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmppath = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        shutil.move(tmppath, path)  # replace atomically
    finally:
        try:
            if os.path.exists(tmppath):
                os.remove(tmppath)
        except Exception:
            pass

def _calls_list() -> List[dict]:
    db = _load_json(CALLS_DB, {"calls": []})
    calls = db.get("calls", [])
    calls.sort(key=lambda c: c.get("created_at") or "", reverse=True)
    return calls

def _calls_upsert(call: dict) -> None:
    db = _load_json(CALLS_DB, {"calls": []})
    by_id = {c.get("call_id"): c for c in db.get("calls", []) if c.get("call_id")}
    by_id[call["call_id"]] = call
    db["calls"] = list(by_id.values())
    _atomic_write_json(CALLS_DB, db)
    print(f"[INFO] calls.json actualizado en {CALLS_DB} (total={len(db['calls'])})")

def _subs_list(user: str) -> List[dict]:
    db = _load_json(SUBS_DB, {"subs": []})
    return [s for s in db.get("subs", []) if s.get("user") == user]

def _subs_append(sub: dict) -> None:
    db = _load_json(SUBS_DB, {"subs": []})
    subs = db.get("subs", [])
    subs.append(sub)
    db["subs"] = subs
    _atomic_write_json(SUBS_DB, db)

# =========================
# App & CORS
# =========================
app = FastAPI(title="Licitante Backend")

ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# WebSocket Manager
# =========================
WS: Dict[str, Set[WebSocket]] = {}
async def ws_emit(user: str, payload: dict):
    for ws in list(WS.get(user, set())):
        try:
            await ws.send_json(payload)
        except Exception:
            pass

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    user = websocket.query_params.get("user")
    if not user:
        await websocket.close(code=4400)
        return
    await websocket.accept()
    WS.setdefault(user, set()).add(websocket)
    try:
        await websocket.send_json({"type": "hello", "user": user})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        WS.get(user, set()).discard(websocket)

# =========================
# Health & Debug
# =========================
@app.get("/health")
def health():
    return {"ok": True, "time": _now_iso()}

@app.get("/debug/paths")
def debug_paths():
    return {
        "DATA_DIR": str(DATA_DIR),
        "CALLS_DB": str(CALLS_DB),
        "SUBS_DB": str(SUBS_DB),
        "calls_db_exists": CALLS_DB.exists(),
        "subs_db_exists": SUBS_DB.exists(),
        "calls_sample": _calls_list()[:3],
    }

@app.on_event("startup")
async def show_routes():
    print("\n=== LICITANTE START ===")
    print(f"DATA_DIR     -> {DATA_DIR}")
    print(f"CALLS_DB     -> {CALLS_DB}")
    print(f"SUBS_DB      -> {SUBS_DB}")
    print(f"SECRET set?  -> {'YES' if bool(LICITANTE_SECRET) else 'NO'}")
    print("=== ROUTES ===")
    for r in app.routes:
        name = r.__class__.__name__
        methods = getattr(r, "methods", None)
        methods_str = ",".join(sorted(methods)) if methods else "-"
        print(f"{r.path:30s}  {methods_str:15s}  {name}")
    print("==============\n")

# =========================
# Calls (recibir por push del Convocante)
# =========================
@app.get("/api/calls")
def list_calls():
    """Listado de convocatorias que el convocante nos envió por push y quedaron persistidas."""
    return {"ok": True, "calls": _calls_list()}

@app.post("/api/calls/sync")
def calls_sync(payload: dict = Body(...)):
    """
    Webhook llamado por el Convocante cuando crea o reanuncia una convocatoria.
    Espera: { "secret": str, "call": { "call_id","key_id","rsa_pub_pem_url","created_at",... } }
    """
    if not LICITANTE_SECRET:
        raise HTTPException(status_code=500, detail="LICITANTE_SECRET not configured")
    if payload.get("secret") != LICITANTE_SECRET:
        raise HTTPException(status_code=403, detail="forbidden")

    c = payload.get("call") or {}
    # validación mínima
    for k in ("call_id", "key_id", "rsa_pub_pem_url"):
        if not c.get(k):
            raise HTTPException(status_code=400, detail=f"missing field in call: {k}")
    if not c.get("created_at"):
        c["created_at"] = _now_iso()

    _calls_upsert(c)
    # (opcional) WS global:
    # await ws_emit("licitante", {"type": "call.sync", "call_id": c["call_id"]})
    return {"ok": True, "stored": c["call_id"]}

# =========================
# Submissions (envío al convocante)
# =========================
@app.get("/api/submissions")
def list_submissions(user: str):
    return {"ok": True, "submissions": _subs_list(user)}

@app.post("/api/submit")
async def submit_package(
    user: str = Form(...),
    sealed: UploadFile | None = File(None),
    # modo piezas (opcionales si vienes con sealed.zip)
    meta: UploadFile | None = File(None),
    payload: UploadFile | None = File(None),
    wrapped_key: UploadFile | None = File(None),
    nonce: UploadFile | None = File(None),
    tag: UploadFile | None = File(None),
):
    """
    Envía la propuesta al Convocante. Puedes:
      1) Enviar 'sealed.zip' (recomendado), o
      2) Enviar las 5 piezas por separado.
    Este backend convierte sealed.zip a piezas si hace falta y reenvía al convocante.
    """
    # 1) Caso sealed.zip
    if sealed is not None:
        buf = await sealed.read()
        try:
            zf = zipfile.ZipFile(io.BytesIO(buf))
        except Exception:
            return {"ok": False, "msg": "sealed.zip inválido"}
        need = ["meta.json", "payload.enc", "wrapped_key.bin", "nonce.bin", "tag.bin"]
        missing = [n for n in need if n not in zf.namelist()]
        if missing:
            return {"ok": False, "msg": f"sealed.zip incompleto: faltan {missing}"}

        files = {
            "meta":        ("meta.json",       zf.read("meta.json"),       "application/json"),
            "payload":     ("payload.enc",     zf.read("payload.enc"),     "application/octet-stream"),
            "wrapped_key": ("wrapped_key.bin", zf.read("wrapped_key.bin"), "application/octet-stream"),
            "nonce":       ("nonce.bin",       zf.read("nonce.bin"),       "application/octet-stream"),
            "tag":         ("tag.bin",         zf.read("tag.bin"),         "application/octet-stream"),
        }

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(CONVOCANTE_URL, files=files)

        ok = (200 <= r.status_code < 300)
        sid = uuid.uuid4().hex[:12]
        now = _now_iso()
        record = {"id": sid, "user": user, "state": "PENDING", "created_at": now, "meta": {}}
        _subs_append(record)
        await ws_emit(user, {"type": "submitted", "submission_id": sid})
        return {"ok": ok, "submission_id": sid, "conv_status": r.status_code}

    # 2) Caso piezas sueltas
    if all([meta, payload, wrapped_key, nonce, tag]):
        meta_b    = await meta.read()
        payload_b = await payload.read()
        wrap_b    = await wrapped_key.read()
        nonce_b   = await nonce.read()
        tag_b     = await tag.read()

        files = {
            "meta":        ("meta.json",       meta_b,    "application/json"),
            "payload":     ("payload.enc",     payload_b, "application/octet-stream"),
            "wrapped_key": ("wrapped_key.bin", wrap_b,    "application/octet-stream"),
            "nonce":       ("nonce.bin",       nonce_b,   "application/octet-stream"),
            "tag":         ("tag.bin",         tag_b,     "application/octet-stream"),
        }

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(CONVOCANTE_URL, files=files)

        ok = (200 <= r.status_code < 300)
        sid = uuid.uuid4().hex[:12]
        now = _now_iso()
        record = {"id": sid, "user": user, "state": "PENDING", "created_at": now, "meta": {}}
        _subs_append(record)
        await ws_emit(user, {"type": "submitted", "submission_id": sid})
        return {"ok": ok, "submission_id": sid, "conv_status": r.status_code}

    return {"ok": False, "msg": "Envía sealed.zip o las 5 piezas requeridas."}
