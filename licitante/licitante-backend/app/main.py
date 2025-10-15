import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ⚙️ Config centralizada (está en app/services/config.py)
from .config import settings

# 🧩 Routers reales (están en app/routes/)
from .routes.health import router as health_router
from .routes.calls import router as calls_router
from .routes.submit import router as submit_router
from .routes.submissions import router as submissions_router
from .routes.notifications import router as notifications_router

app = FastAPI(title=settings.APP_NAME)

# ✅ CORS robusto: soporta "*" o lista separada por comas
origins = [o.strip() for o in (settings.CORS_ORIGINS or "").split(",") if o.strip()]
allow_origin_regex = ".*" if origins == ["*"] else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=[] if allow_origin_regex else origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health sin prefijo (coincide con tu router /health)
app.include_router(health_router)

# ✅ Montaje de todos los endpoints del licitante bajo /licitante
#    (cada router ya usa prefix="/api" adentro, quedará /licitante/api/...)
app.include_router(calls_router,         prefix=settings.API_PREFIX)
app.include_router(submit_router,        prefix=settings.API_PREFIX)
app.include_router(submissions_router,   prefix=settings.API_PREFIX)
app.include_router(notifications_router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    # ▶️ Ejecuta uvicorn desde la carpeta que contiene "app/"
    uvicorn.run(
        "app.main:app",
        host=os.getenv("LICITANTE_HOST", "127.0.0.1"),
        port=int(os.getenv("LICITANTE_PORT", 8002)),
        reload=True,
    )
