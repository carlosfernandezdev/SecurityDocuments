# ed25519_gen.py
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def main(out_dir=".", name="ed25519"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    sk = ed25519.Ed25519PrivateKey.generate()
    pk = sk.public_key()

    sk_pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pk_pem = pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    (out / f"{name}_priv.pem").write_bytes(sk_pem)
    (out / f"{name}_pub.pem").write_bytes(pk_pem)
    print("[OK] Generadas:")
    print("  -", out / f"{name}_priv.pem")
    print("  -", out / f"{name}_pub.pem")

if __name__ == "__main__":
    main()
