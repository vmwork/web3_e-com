from datetime import datetime, timedelta, timezone  # 🟢 Добавили timezone
from typing import Optional
from jose import JWTError, jwt
from eth_account.messages import encode_defunct
from eth_account import Account
from core.config import settings  # 🟢 ИСПРАВИЛИ: убрали префикс app.

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # 🟢 Заменили устаревший utcnow() на правильный стандарт Python 3.12
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


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        wallet_address: str = payload.get("sub")
        return wallet_address
    except JWTError:
        return None
