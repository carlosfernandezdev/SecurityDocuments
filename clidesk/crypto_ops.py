# crypto_ops.py
import json
import zipfile
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from typing import List, Union, Dict, Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

CHUNK = 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def build_manifest(files: List[Path]) -> Dict[str, Any]:
    return {
        "version": 1,
        "files": [{"path": p.name, "sha256": sha256_file(p)} for p in files],
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


def run_encrypt_and_sign(
    input_files: List[Union[str, Path]],
    rsa_pub_pem: bytes,
    ed_priv_pem: bytes,
    output_dir: Union[str, Path],
    bidder: Dict[str, str],
    call_id: str,
    key_id: str,
) -> Dict[str, Any]:
    """
    Produce EXACTAMENTE estas salidas (que el convocante espera):
      - meta.json
      - payload.enc    (ciphertext AES-256-GCM, SIN tag)
      - wrapped_key.bin
      - nonce.bin      (12 bytes)
      - tag.bin        (16 bytes)
      - sealed.zip     (opcional: paquete contenedor de las 5 piezas anteriores)

    El plaintext cifrado (AES-GCM) es un ZIP ("sealed_base.zip") con:
      - content.zip
      - manifest.json
      - signature.bin   (firma Ed25519 sobre content.zip)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- 1) content.zip con los archivos de entrada ---
    files = [Path(p) for p in input_files]
    for p in files:
        if not p.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {p}")

    content_zip = output_dir / "content.zip"
    with zipfile.ZipFile(content_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            z.write(p, arcname=p.name)

    # --- 2) manifest.json con hashes SHA-256 ---
    manifest = build_manifest(files)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # --- 3) Firma Ed25519 sobre content.zip ---
    priv = serialization.load_pem_private_key(ed_priv_pem, password=None)
    if not isinstance(priv, ed25519.Ed25519PrivateKey):
        raise ValueError("La clave privada NO es Ed25519 (se esperaba Ed25519).")
    signature = priv.sign(content_zip.read_bytes())
    (output_dir / "signature.bin").write_bytes(signature)

    # Pública Ed25519 (opcional en meta para que el convocante pueda verificar)
    ed_pub_hex = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()

    # --- 4) sealed_base.zip = ZIP claro con 3 archivos requeridos ---
    sealed_base = output_dir / "sealed_base.zip"
    with zipfile.ZipFile(sealed_base, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(content_zip,   arcname="content.zip")
        z.write(manifest_path, arcname="manifest.json")
        z.writestr("signature.bin", signature)

    # --- 5) AES-256-GCM: ciphertext SIN tag; tag separado ---
    K = secrets.token_bytes(32)          # 32B = AES-256
    nonce = secrets.token_bytes(12)      # GCM nonce 96 bits
    cipher = Cipher(algorithms.AES(K), modes.GCM(nonce), backend=default_backend())
    enc = cipher.encryptor()
    plaintext = sealed_base.read_bytes()
    ciphertext = enc.update(plaintext) + enc.finalize()
    tag = enc.tag  # 16B

    (output_dir / "payload.enc").write_bytes(ciphertext)   # SIN tag
    (output_dir / "nonce.bin").write_bytes(nonce)
    (output_dir / "tag.bin").write_bytes(tag)

    # --- 6) Envolver K con RSA-OAEP-SHA256 ---
    pub = serialization.load_pem_public_key(rsa_pub_pem)
    if not isinstance(pub, rsa.RSAPublicKey):
        raise ValueError("La clave pública NO es RSA.")
    wrapped = pub.encrypt(
        K,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )
    (output_dir / "wrapped_key.bin").write_bytes(wrapped)

    # --- 7) meta.json con identificadores, algoritmos y hashes ---
    meta = {
        "version": 1,
        "call_id": call_id,
        "key_id": key_id,
        "alg": {
            "aead": "AES-256-GCM",
            "wrap": "RSA-OAEP-SHA256",
            "sig": "Ed25519",
            "hash": "SHA-256"
        },
        "bidder": {
            "name": bidder.get("name", ""),
            "identifier": bidder.get("identifier", ""),
            "ed25519_pk_hex": ed_pub_hex,   # opcional pero muy útil
        },
        "payload_sha256": sha256_file(output_dir / "payload.enc"),
        "content_zip_sha256": sha256_file(content_zip),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    meta_path = output_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # --- 8) (opcional) sealed.zip con las 5 piezas para transporte sencillo ---
    sealed_final = output_dir / "sealed.zip"
    with zipfile.ZipFile(sealed_final, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(meta_path,                         arcname="meta.json")
        z.write(output_dir / "payload.enc",        arcname="payload.enc")
        z.write(output_dir / "wrapped_key.bin",    arcname="wrapped_key.bin")
        z.write(output_dir / "nonce.bin",          arcname="nonce.bin")
        z.write(output_dir / "tag.bin",            arcname="tag.bin")

    # Añadir el hash del sealed.zip al meta (si lo quieres para control)
    meta_json = json.loads(meta_path.read_text(encoding="utf-8"))
    meta_json["sealed_zip_sha256"] = sha256_file(sealed_final)
    meta_path.write_text(json.dumps(meta_json, indent=2), encoding="utf-8")

    outputs = [
        "meta.json", "payload.enc", "wrapped_key.bin", "nonce.bin", "tag.bin", "sealed.zip"
    ]
    return {"output_dir": str(output_dir), "outputs": outputs}
