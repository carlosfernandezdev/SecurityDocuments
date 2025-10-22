import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Convocatorias")
    SECRET_TOKEN: str = os.getenv("SECRET_TOKEN", "change-me")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:0209@localhost:5433/convocatorias")

settings = Settings()
