from pydantic import BaseModel
from typing import Optional


class RelayResponse(BaseModel):
    success: bool
    answer: Optional[str] = None
    provider_used: str
    error_msg: Optional[str] = None
