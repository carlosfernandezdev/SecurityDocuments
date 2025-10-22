from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base
import enum

class Role(str, enum.Enum):
    CONVOCANTE = "CONVOCANTE"
    LICITANTE  = "LICITANTE"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(320), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.LICITANTE)
    password_hash = Column(String(200), nullable=False)

    convocatorias = relationship("Convocatoria", back_populates="owner")
    submissions   = relationship("Submission", back_populates="licitante")

class Convocatoria(Base):
    __tablename__ = "convocatorias"
    id = Column(Integer, primary_key=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="convocatorias")

    submissions = relationship("Submission", back_populates="convocatoria")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    convocatoria_id = Column(Integer, ForeignKey("convocatorias.id"), nullable=False)
    licitante_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    payload_sha256 = Column(String(64))
    content_zip_sha256 = Column(String(64))
    sealed_zip_sha256 = Column(String(64))

    wrapped_key = Column(LargeBinary, nullable=False)
    nonce       = Column(LargeBinary, nullable=False)
    tag         = Column(LargeBinary, nullable=False)
    ciphertext  = Column(LargeBinary, nullable=False)

    signer_pk_hex = Column(String(64))
    signature     = Column(LargeBinary)

    convocatoria = relationship("Convocatoria", back_populates="submissions")
    licitante    = relationship("User", back_populates="submissions")
