from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from config import CORS_ALLOW_ORIGINS, APP_PREFIX, PUBLIC_DIR, LICITANTE_CALLBACKS, LICITANTE_SECRET
from routes.calls import router as calls_router
from routes.internal import router as internal_router
from public_api import router as public_router

app = FastAPI(title="Convocante")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estáticos (sirve /convocante/public/keys/<call_id>/rsa_pub.pem)
app.mount(f"{APP_PREFIX}/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")

# Routers
app.include_router(calls_router)
app.include_router(internal_router)
app.include_router(public_router)

# Estado para push a licitantes
app.state.licitante_callbacks = LICITANTE_CALLBACKS
app.state.licitante_secret = LICITANTE_SECRET
