# Backend CONVOCANTE

- Login por cookies + bcrypt (sin JWT)
- CRUD de convocatorias (crear/listar/detalle)
- WebSocket `/ws/licitante` para avisar nuevas convocatorias
- `POST /api/submissions/{conv_id}/{sub_id}/decrypt` para descifrar propuestas
- Opcionalmente acepta `POST /api/submissions/{conv_id}` si el licitante decide golpear esta URL

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
uvicorn app.main:app --reload --port 8001
```
