import os
from pathlib import Path

class Settings:
    APP_NAME: str = "Convocante API"
    API_PREFIX: str = "/convocante"
    SECRET_TOKEN: str = os.getenv("CONVOCANTE_SHARED_SECRET", "SHARED_SECRET")
    STORAGE_BASE: Path = Path(os.getenv("STORAGE_BASE", "storage")).resolve()
    INBOX_DIR: Path = STORAGE_BASE / "inbox"
    PROCESSED_DIR: Path = STORAGE_BASE / "processed"
    QUARANTINE_DIR: Path = STORAGE_BASE / "quarantine"
    KEYS_DIR: Path = Path(os.getenv("KEYS_DIR", "keys")).resolve()
    # CORS
    # app/config.py
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:5174,http://localhost:5174"
    )

    # Limits
    MAX_PAYLOAD_MB: int = int(os.getenv("MAX_PAYLOAD_MB", "200"))
    LICITANTE_BASE = os.getenv("LICITANTE_BASE", "http://127.0.0.1:8002/licitante")
    LICITANTE_CREDENTIALS_JSON = os.getenv("LICITANTE_CREDENTIALS_JSON", "{}")

settings = Settings()
