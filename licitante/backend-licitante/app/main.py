from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import Base, engine
from .auth.router import router as auth_router
from .convocatorias.router import router as conv_router
from .submissions.router import router as sub_router

app = FastAPI(title=settings.APP_NAME + " - LICITANTE")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api")
app.include_router(conv_router, prefix="/api")
app.include_router(sub_router, prefix="/api")
