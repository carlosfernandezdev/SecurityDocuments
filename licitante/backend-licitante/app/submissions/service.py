import base64
from ..crypto_utils import rsa_decrypt_oaep_sha256, aes_gcm_decrypt, ed25519_verify

def b64d(s: str) -> bytes: return base64.b64decode(s)

def decrypt_envelope(private_pem: bytes, wrapped_key: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> bytes:
    aes_key = rsa_decrypt_oaep_sha256(private_pem, wrapped_key)
    return aes_gcm_decrypt(aes_key, nonce, tag, ciphertext)

def verify_optional_signature(signer_pk_hex: str | None, message: bytes, signature: bytes | None) -> bool:
    if not signer_pk_hex or not signature:
        return True
    return ed25519_verify(signer_pk_hex, message, signature)
