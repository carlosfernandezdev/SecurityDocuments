# clidesk — empaquetado de propuesta (AES-GCM + RSA-OAEP + Ed25519)

## Salida esperada
Dentro de `proposal_YYYY-mm-ddTHH-MM-SSZ/`:
- `sealed.zip`  **(SUBIR a la web)**
- `meta.json`, `payload.enc`, `wrapped_key.bin`, `nonce.bin`, `tag.bin`  *(copias locales)*
- `content.zip`, `manifest.json`, `signature.bin`  *(auditoría local)*

Contenido **dentro de `sealed.zip`**:
