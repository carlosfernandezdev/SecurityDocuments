# Convocante Backend (FastAPI)

## Requisitos
- Python 3.10+
- `pip install -r requirements.txt`

## Variables de entorno
Crea `.env` (o exporta) con:
```
CONVOCANTE_SHARED_SECRET=SHARED_SECRET
STORAGE_BASE=storage
KEYS_DIR=keys
CORS_ORIGINS=*
MAX_PAYLOAD_MB=200
```

## Ejecutar
```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

## Endpoints clave
- `GET  /convocante/health`
- `POST /convocante/api/calls`
- `GET  /convocante/api/calls`
- `GET  /convocante/api/keys/{key_id}/rsa_pub.pem`
- `POST /convocante/internal/receive-proposal?secret=SHARED_SECRET` (multipart)

## Claves RSA
Genera un par para `key_id=default`:
```
python generate_rsa.py --key-id default
```
Esto crea `keys/default_rsa_priv.pem` y `keys/default_rsa_pub.pem`.

## Flujo de prueba (cURL)
1) Crear convocatoria:
```
curl -s -X POST http://127.0.0.1:8001/convocante/api/calls   -H "Content-Type: application/json"   -d '{ "call_id": "TEST-001", "key_id":"default", "rsa_pub_pem": "'"$(cat keys/default_rsa_pub.pem | sed ':a;N;$!ba;s/\n/\\n/g')"'" }'
```

2) Descargar pública (para tu app de escritorio):
```
curl -s http://127.0.0.1:8001/convocante/api/keys/default/rsa_pub.pem
```

3) Envío de propuesta (multipart):
```
curl -s -X POST "http://127.0.0.1:8001/convocante/internal/receive-proposal?secret=SHARED_SECRET"   -F meta=@meta.json   -F payload=@payload.enc   -F wrapped_key=@wrapped_key.bin   -F nonce=@nonce.bin   -F tag=@tag.bin
```

El resultado se guarda en `storage/inbox/` y `storage/processed/`.
