import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class UserConfigBase(BaseModel):
    theme: Optional[str] = "system"
    language: Optional[str] = "en"
    timezone: Optional[str] = "UTC"
    notifications: Optional[Dict[str, Any]] = None
    privacy: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    additional_metadata: Optional[Dict[str, Any]] = None

class UserConfigCreate(UserConfigBase):
    pass

class UserConfigUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    notifications: Optional[Dict[str, Any]] = None
    privacy: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    additional_metadata: Optional[Dict[str, Any]] = None

class ShowUserConfig(UserConfigBase):
    id: uuid.UUID  # 🟢 Было int. Теперь нативный UUID v7
    user_id: str   # 🟢 Было int. Теперь строковый wallet_address кошелька
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
