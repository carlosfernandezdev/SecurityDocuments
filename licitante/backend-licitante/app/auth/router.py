from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from itsdangerous import URLSafeSerializer, BadSignature
from ..db import get_db
from ..models import User
from ..schemas import UserCreate, UserOut, LoginIn
from .password import hash_password, verify_password
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
ser = URLSafeSerializer(settings.SECRET_TOKEN, salt="session")
SESSION_COOKIE = "session"

def get_current_user(req: Request, db: Session) -> User | None:
    token = req.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        data = ser.loads(token)
        return db.get(User, int(data["uid"]))
    except BadSignature:
        return None

@router.post("/register", response_model=UserOut)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=body.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = User(email=body.email, name=body.name, role=body.role, password_hash=hash_password(body.password))
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=UserOut)
def login(body: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    cookie = ser.dumps({"uid": user.id})
    response.set_cookie("session", cookie, httponly=True, samesite="lax")
    return user

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session")
    return {"ok": True}
