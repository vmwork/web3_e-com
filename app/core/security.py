from datetime import datetime, timedelta, timezone 
from typing import Optional, Union
from jose import JWTError, jwt
from eth_account.messages import encode_defunct
from eth_account import Account
from core.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_wallet_signature(wallet_address: str, message: str, signature: str) -> bool:
    try:
        message_hash = encode_defunct(text=message)
        recovered_address = Account.recover_message(message_hash, signature=signature)
        return recovered_address.lower() == wallet_address.lower()
    except Exception:
        return False


def verify_token(token: str) -> Optional[Union[str, dict]]:
    """
    Декодирует JWT токен и возвращает payload.
    Поддерживает как wallet_address, так и user_id.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)