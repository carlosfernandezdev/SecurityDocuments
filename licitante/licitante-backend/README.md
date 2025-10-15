# Licitante Web — Backend (FastAPI)
Run:
```
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```
Env:
```
CONVOCANTE_BASE=http://127.0.0.1:8001/convocante
CONVOCANTE_SHARED_SECRET=SHARED_SECRET
STORAGE_BASE=storage
CORS_ORIGINS=*
```