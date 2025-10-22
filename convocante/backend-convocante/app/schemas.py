from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str  # "CONVOCANTE" | "LICITANTE"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str
    class Config:
        orm_mode = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ConvocatoriaIn(BaseModel):
    titulo: str
    descripcion: str

class ConvocatoriaOut(BaseModel):
    id: int
    titulo: str
    descripcion: str
    owner_id: int
    class Config:
        orm_mode = True

class SubmissionIn(BaseModel):
    payload_sha256: Optional[str] = None
    content_zip_sha256: Optional[str] = None
    sealed_zip_sha256: Optional[str] = None
    wrapped_key_b64: str
    nonce_b64: str
    tag_b64: str
    ciphertext_b64: str
    signer_pk_hex: Optional[str] = None
    signature_b64: Optional[str] = None

class SubmissionOut(BaseModel):
    id: int
    convocatoria_id: int
    licitante_id: int
    class Config:
        orm_mode = True
