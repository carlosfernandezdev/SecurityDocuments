import os
from pathlib import Path

class Settings:
    APP_NAME = "Licitante API"
    API_PREFIX = "/licitante"

    # Almacenamiento local
    STORAGE_BASE: Path = Path(os.getenv("STORAGE_BASE", "storage")).resolve()
    SUBMISSIONS_DIR: Path = STORAGE_BASE / "submissions"
    NOTIFICATIONS_DIR: Path = STORAGE_BASE / "notifications"
    ACCOUNTS_FILE: Path = STORAGE_BASE / "accounts.json"  # ← necesario para Basic Auth
    
    # callback básico hacia este mismo licitante (el convocante usará esto)
    LICITANTE_BASE = "http://127.0.0.1:8002/licitante"
    CALLBACK_SELECTION_URL = f"{LICITANTE_BASE}/api/notifications/selection"

    # credenciales TÉCNICAS para que el convocante te notifique (NO de usuario final)
    CALLBACK_AUTH_SCHEME = "basic"       # o "bearer"
    CALLBACK_AUTH_USERNAME = "convocante-bot"
    CALLBACK_AUTH_PASSWORD = "SECRETO_SUPER"   # o token si usas bearer

    # Llamadas al Convocante (para reenviar propuestas)
    CONVOCANTE_BASE = os.getenv("CONVOCANTE_BASE", "http://127.0.0.1:8001/convocante")
    CONVOCANTE_SHARED_SECRET = os.getenv("CONVOCANTE_SHARED_SECRET", "SHARED_SECRET")

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

settings = Settings()
