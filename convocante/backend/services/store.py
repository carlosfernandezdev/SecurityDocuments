import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from config import DATA_DIR, CALLS_DIR, PUBLIC_DIR, APP_PREFIX

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def call_dir(call_id: str) -> Path:
    d = CALLS_DIR / call_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "submissions").mkdir(parents=True, exist_ok=True)
    return d

def save_call_files(call_id: str, key_id: str = "default") -> Dict[str, Any]:
    d = call_dir(call_id)

    # Generar par RSA
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    pub_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Guardar en calls/<id>
    (d / "rsa_priv.pem").write_bytes(priv_pem)
    (d / "rsa_pub.pem").write_bytes(pub_pem)
    (d / "key_id.txt").write_text(key_id, encoding="utf-8")
    meta = {"call_id": call_id, "key_id": key_id, "created_at": now_iso()}
    (d / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # Publicar a /public/keys/<id>
    pub_target = PUBLIC_DIR / "keys" / call_id
    pub_target.mkdir(parents=True, exist_ok=True)
    (pub_target / "rsa_pub.pem").write_bytes(pub_pem)

    return {
        "call_id": call_id,
        "key_id": key_id,
        "rsa_pub_pem_url": f"{APP_PREFIX}/public/keys/{call_id}/rsa_pub.pem",
        "created_at": meta["created_at"],
    }

def list_calls() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if not CALLS_DIR.exists():
        return out
    for p in CALLS_DIR.iterdir():
        if not p.is_dir():
            continue
        call_id = p.name
        key_id = (p / "key_id.txt").read_text(encoding="utf-8").strip() if (p / "key_id.txt").exists() else "default"
        try:
            created = json.loads((p / "meta.json").read_text(encoding="utf-8")).get("created_at")
        except Exception:
            created = now_iso()
        out.append({
            "call_id": call_id,
            "key_id": key_id,
            "rsa_pub_pem_url": f"{APP_PREFIX}/public/keys/{call_id}/rsa_pub.pem",
            "created_at": created,
        })
    out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return out

def persist_submission(call_id: str, submission_id: str, files: Dict[str, bytes], state: Dict[str, Any]) -> Path:
    """
    Persiste una propuesta bajo: calls/<call_id>/submissions/<submission_id>/
      - guarda todos los 'files' (dict nombre->bytes)
      - guarda state.json con metadatos/validaciones
    """
    subdir = call_dir(call_id) / "submissions" / submission_id
    subdir.mkdir(parents=True, exist_ok=True)

    # Escribir piezas
    for name, content in files.items():
        (subdir / name).write_bytes(content)

    # Guardar estado
    (subdir / "state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return subdir
