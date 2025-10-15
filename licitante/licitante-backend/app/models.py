from pydantic import BaseModel, Field
from typing import Optional

class SubmissionRecord(BaseModel):
    id: str
    call_id: str
    bidder_identifier: Optional[str] = None
    status: str
    created_at: str
    response: Optional[dict] = None

class SelectionNotification(BaseModel):
    call_id: str
    bidder_identifier: str
    decision: str = Field(..., pattern="^(accepted|rejected)$")
    notes: Optional[str] = None