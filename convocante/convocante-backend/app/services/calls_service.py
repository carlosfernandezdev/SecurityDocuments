from pathlib import Path
from typing import Dict
from datetime import datetime
import json, os, secrets

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from ..config import settings

CALLS_DB = settings.STORAGE_BASE / "calls.json"

def _load() -> Dict:
    if CALLS_DB.exists():
        return json.loads(CALLS_DB.read_text(encoding="utf-8"))
    return {"calls": []}

def _save(doc: Dict):
    CALLS_DB.parent.mkdir(parents=True, exist_ok=True)
    CALLS_DB.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")

def get_pubkey_path(key_id: str) -> Path:
    return settings.KEYS_DIR / key_id / "rsa_pub.pem"

def get_privkey_path(key_id: str) -> Path:
    return settings.KEYS_DIR / key_id / "rsa_priv.pem"

def _call_exists(call_id: str) -> bool:
    return any(c["call_id"] == call_id for c in _load()["calls"])

def _make_key_id(call_id: str) -> str:
    # Ej: call-TEST-001-20251014-153012-3f7a
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    rnd = secrets.token_hex(2)  # 4 hex = 2 bytes
    safe_call = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in call_id)
    return f"call-{safe_call}-{ts}-{rnd}"

def _generate_rsa_pair(key_id: str, bits: int = 3072):
    keydir = settings.KEYS_DIR / key_id
    keydir.mkdir(parents=True, exist_ok=True)

    priv = rsa.generate_private_key(public_exponent=65537, key_size=bits)
    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_pem = priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    (keydir / "rsa_priv.pem").write_bytes(priv_pem)
    (keydir / "rsa_pub.pem").write_bytes(pub_pem)


def add_call(call_id: str) -> Dict:
    # Política: call_id único. Si quieres permitir versiones, cámbialo aquí.
    if _call_exists(call_id):
        raise ValueError(f"call_id '{call_id}' ya existe")

    key_id = _make_key_id(call_id)
    _generate_rsa_pair(key_id)

    doc = _load()
    doc["calls"].append({
        "call_id": call_id,
        "key_id": key_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "active"
    })
    _save(doc)
    return {"call_id": call_id, "key_id": key_id}
def list_calls():
    return _load()["calls"]