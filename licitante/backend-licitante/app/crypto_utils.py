from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import binascii, hashlib

def rsa_decrypt_oaep_sha256(private_pem: bytes, wrapped_key: bytes) -> bytes:
    private_key = serialization.load_pem_private_key(private_pem, password=None)
    return private_key.decrypt(
        wrapped_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

def aes_gcm_decrypt(aes_key: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> bytes:
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(nonce, ciphertext + tag, None)

def ed25519_verify(pub_key_hex: str, message: bytes, signature: bytes) -> bool:
    try:
        pk = Ed25519PublicKey.from_public_bytes(binascii.unhexlify(pub_key_hex))
        pk.verify(signature, message)
        return True
    except Exception:
        return False

def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()
