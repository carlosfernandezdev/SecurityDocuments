from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes.health import router as health_router
from .routes.submissions import router as submissions_router
from .routes.calls import router as calls_router
from .routes.keys import router as keys_router
from .routes.receive import router as receive_router
from .storage import ensure_dirs

app = FastAPI(title=settings.APP_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(calls_router, prefix=settings.API_PREFIX)
app.include_router(keys_router, prefix=settings.API_PREFIX)
app.include_router(receive_router, prefix=settings.API_PREFIX)
app.include_router(submissions_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
def startup():
    ensure_dirs()
