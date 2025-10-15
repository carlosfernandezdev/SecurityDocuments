from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class CallIn(BaseModel):
    call_id: str = Field(..., examples=["TEST-001"])

class CallOut(BaseModel):
    call_id: str
    key_id: str

class MetaBidder(BaseModel):
    name: str
    identifier: str
    ed25519_pk_hex: str

class MetaAlg(BaseModel):
    aead: str
    wrap: str
    sig: str
    hash: str

class MetaJson(BaseModel):
    version: int
    call_id: str
    key_id: str
    alg: MetaAlg
    bidder: MetaBidder
    payload_sha256: Optional[str] = None
    content_zip_sha256: Optional[str] = None
    sealed_zip_sha256: Optional[str] = None
    timestamp: Optional[str] = None

class SubmissionOut(BaseModel):
    status: str
    call_id: str
    key_id: str
    content_zip_sha256: Optional[str] = None
