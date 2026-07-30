from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum


class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    PENDING = "pending"
    DANGER = "danger"


class WalletTypeEnum(str, Enum):
    EVM = "EVM"
    SOLANA = "SOLANA"
    TRON = "TRON"


class SubscriptionTypeEnum(str, Enum):
    FREE = "free"
    PRO = "pro"
    STUDIO = "studio"


class UserBase(BaseModel):
    wallet_address: str = Field(..., min_length=20, max_length=100)
    wallet_type: WalletTypeEnum = Field(default=WalletTypeEnum.EVM)
    display_name: Optional[str] = Field(None, max_length=50)

class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6)
    display_name: Optional[str] = Field(None, max_length=50)
    wallet_address: Optional[str] = Field(None, min_length=20, max_length=100)

class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    wallet_address: str = Field(..., min_length=20, max_length=100)
    wallet_type: WalletTypeEnum = Field(default=WalletTypeEnum.EVM)
    display_name: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    hashed_password: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    is_email_verified: Optional[bool] = None


class ShowUser(BaseModel):
    id: UUID  # ✅ Добавили UUID
    wallet_address: str
    wallet_type: WalletTypeEnum
    email: Optional[str] = None
    is_email_verified: bool
    has_paid_entrance: bool
    paid_entrance_at: Optional[datetime] = None
    total_slots: int
    used_slots: int
    rating: float
    total_deals: int
    positive_deals: int
    subscription_type: SubscriptionTypeEnum
    subscription_until: Optional[datetime] = None
    fee_percent: int
    status: UserStatusEnum
    role: str
    display_name: Optional[str] = None
    first_seen: datetime
    last_active: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConnectRequest(BaseModel):
    wallet_address: str = Field(..., min_length=20, max_length=100)
    message: str
    signature: str


class TestConnectRequest(BaseModel):
    wallet_address: str = Field(..., min_length=20, max_length=100)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: ShowUser