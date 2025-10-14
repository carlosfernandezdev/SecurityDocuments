from pathlib import Path

# —— AJUSTA SOLO ESTAS CONSTANTES —— #
APP_PREFIX = "/convocante"

# Carpetas
BASE_DIR  = Path(__file__).resolve().parent
DATA_DIR  = (BASE_DIR / "data").resolve()          # << dónde guarda todo
CALLS_DIR = (DATA_DIR / "calls").resolve()
PUBLIC_DIR= (DATA_DIR / "public").resolve()

# CORS (frentes permitidos)
CORS_ALLOW_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

# Secreto para /convocante/internal/receive-proposal (cuando licitante envía propuestas)
INTERNAL_SECRET = "SHARED_SECRET"

# Push a licitantes (webhook)
LICITANTE_CALLBACKS = ["http://127.0.0.1:8002"]     # puedes poner más URLs
LICITANTE_SECRET    = "UN_SECRETO_COMPARTIDO"
# ———————————————————————————————— #

# Crear carpetas si no existen
DATA_DIR.mkdir(parents=True, exist_ok=True)
CALLS_DIR.mkdir(parents=True, exist_ok=True)
(PUBLIC_DIR / "keys").mkdir(parents=True, exist_ok=True)
