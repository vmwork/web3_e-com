import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class ProfileBase(BaseModel):
    bio: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    extra_data: Optional[Dict[str, Any]] = None

class ProfileCreate(ProfileBase):
    user_id: str  # 🟢 Было int. Теперь str, так как это wallet_address

class ProfileUpdate(ProfileBase):
    pass

class ShowProfile(ProfileBase):
    id: uuid.UUID  # 🟢 Было int. Теперь нативный UUID v7
    user_id: str   # 🟢 Было int. Теперь адрес кошелька (str)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
