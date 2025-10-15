from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-id", required=True)
    parser.add_argument("--bits", type=int, default=3072)
    parser.add_argument("--out", default="keys")
    args = parser.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    priv = rsa.generate_private_key(public_exponent=65537, key_size=args.bits)
    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub = priv.public_key()
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    (out / f"{args.key_id}_rsa_priv.pem").write_bytes(priv_pem)
    (out / f"{args.key_id}_rsa_pub.pem").write_bytes(pub_pem)
    print(f"Wrote {out}/{args.key_id}_rsa_priv.pem and {out}/{args.key_id}_rsa_pub.pem")

if __name__ == "__main__":
    main()
