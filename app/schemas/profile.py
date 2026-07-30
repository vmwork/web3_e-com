import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class ProfileBase(BaseModel):
    bio: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    extra_data: Optional[Dict[str, Any]] = None


class ProfileCreate(ProfileBase):
    user_id: uuid.UUID  # ✅ Теперь UUID


class ProfileUpdate(ProfileBase):
    pass


class ShowProfile(ProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID  # ✅ Теперь UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True