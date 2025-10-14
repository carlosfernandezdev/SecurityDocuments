import hashlib
from typing import Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def rsa_oaep_unwrap(private_pem: bytes, wrapped_key: bytes) -> bytes:
    priv = serialization.load_pem_private_key(private_pem, password=None)
    if not isinstance(priv, rsa.RSAPrivateKey):
        raise ValueError("Private key is not RSA")
    return priv.decrypt(
        wrapped_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

def aes_gcm_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: Optional[bytes] = None) -> bytes:
    # tag provided separately -> concat for AESGCM API (expects together)
    ct_with_tag = ciphertext + tag
    aes = AESGCM(key)
    return aes.decrypt(nonce, ct_with_tag, aad)

def ed25519_verify_hex(pub_hex: str, message: bytes, signature: bytes) -> bool:
    try:
        pk = bytes.fromhex(pub_hex)
        pub = ed25519.Ed25519PublicKey.from_public_bytes(pk)
        pub.verify(signature, message)
        return True
    except Exception:
        return False
