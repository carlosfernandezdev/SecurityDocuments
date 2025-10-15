from cryptography.hazmat.primitives.asymmetric import padding, ed25519
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidSignature
from pathlib import Path
import hashlib

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def rsa_decrypt_oaep_sha256(private_pem_bytes: bytes, wrapped: bytes) -> bytes:
    private_key = serialization.load_pem_private_key(private_pem_bytes, password=None)
    return private_key.decrypt(
        wrapped,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def aes_gcm_decrypt(key: bytes, nonce: bytes, tag: bytes, ciphertext: bytes) -> bytes:
    decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag)).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def ed25519_verify(pubkey_hex: str, message: bytes, signature: bytes) -> bool:
    try:
        pub = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(pubkey_hex))
        pub.verify(signature, message)
        return True
    except InvalidSignature:
        return False
