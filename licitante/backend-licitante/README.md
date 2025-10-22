# Backend LICITANTE

- Login por cookies + bcrypt (sin JWT)
- Convocatorias solo lectura (listar/detalle)
- `POST /api/submissions/{conv_id}` para subir propuestas cifradas (envelope: RSA-OAEP + AES-GCM)
- **Sin WebSocket** aquí: el frontend del licitante debe conectarse al WS del backend CONVOCANTE (`ws://host:8001/ws/licitante`).

## .env ejemplo
```
APP_NAME="Convocatorias"
SECRET_TOKEN="cambia-esto"
CORS_ORIGINS="http://localhost:5173,http://localhost:3000"
DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/convocatorias"
```

## Ejecutar
```
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```
