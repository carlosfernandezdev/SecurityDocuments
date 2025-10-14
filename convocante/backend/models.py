from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CallInfo(BaseModel):
    call_id: str
    key_id: str = "default"
    rsa_pub_pem_url: str
    created_at: str

class SubmissionState(BaseModel):
    id: str
    call_id: str
    ok_unwrap: bool
    ok_decrypt: bool
    ok_signature: Optional[bool] = None
    payload_sha256_meta: Optional[str] = None
    payload_sha256_got: Optional[str] = None
    content_files: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)
