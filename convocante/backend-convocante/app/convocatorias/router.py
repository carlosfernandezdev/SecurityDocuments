from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Convocatoria, User, Role
from ..schemas import ConvocatoriaIn, ConvocatoriaOut
from ..auth.router import get_current_user
from ..ws.hub import hub

router = APIRouter(prefix="/convocatorias", tags=["convocatorias"])

@router.post("", response_model=ConvocatoriaOut)
async def crear_convocatoria(body: ConvocatoriaIn, req: Request, db: Session = Depends(get_db)):
    user = get_current_user(req, db)
    if not user or user.role != Role.CONVOCANTE:
        raise HTTPException(status_code=403, detail="Solo convocantes")
    c = Convocatoria(titulo=body.titulo, descripcion=body.descripcion, owner_id=user.id)
    db.add(c); db.commit(); db.refresh(c)
    await hub.broadcast({"type": "new_convocatoria", "id": c.id, "titulo": c.titulo})
    return c

@router.get("", response_model=list[ConvocatoriaOut])
def listar(db: Session = Depends(get_db)):
    return db.query(Convocatoria).order_by(Convocatoria.id.desc()).all()

@router.get("/{conv_id}", response_model=ConvocatoriaOut)
def detalle(conv_id: int, db: Session = Depends(get_db)):
    c = db.get(Convocatoria, conv_id)
    if not c: raise HTTPException(status_code=404, detail="No existe")
    return c
