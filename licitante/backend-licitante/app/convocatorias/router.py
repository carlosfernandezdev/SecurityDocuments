from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Convocatoria
from ..schemas import ConvocatoriaOut

router = APIRouter(prefix="/convocatorias", tags=["convocatorias"])

@router.get("", response_model=list[ConvocatoriaOut])
def listar(db: Session = Depends(get_db)):
    return db.query(Convocatoria).order_by(Convocatoria.id.desc()).all()

@router.get("/{conv_id}", response_model=ConvocatoriaOut)
def detalle(conv_id: int, db: Session = Depends(get_db)):
    c = db.get(Convocatoria, conv_id)
    if not c: raise HTTPException(status_code=404, detail="No existe")
    return c
