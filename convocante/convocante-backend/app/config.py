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
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    # Limits
    MAX_PAYLOAD_MB: int = int(os.getenv("MAX_PAYLOAD_MB", "200"))

settings = Settings()
