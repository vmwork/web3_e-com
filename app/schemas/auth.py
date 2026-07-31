# app/schemas/auth.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
class AuthStatusResponse(BaseModel):
    authenticated: bool = True
    user_id: str
    wallet_address: Optional[str] = None
    email: Optional[str] = None
    role: str
    token_expires_in: int
    scopes: List[str] = ["read", "write"]
    last_active: Optional[datetime] = None