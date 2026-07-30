from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # 🟢 Меняем схему
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User, UserStatus
from core.security import verify_token

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Залежність для вилучення поточного користувача за Web3 JWT-токеном.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate Web3 credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 🟢 Извлекаем сам токен из объекта credentials
    token = credentials.credentials

    wallet_address = verify_token(token)
    if wallet_address is None:
        raise credentials_exception

    user = db.query(User).filter(User.wallet_address == wallet_address).first()
    if user is None:
        raise credentials_exception

    if user.status == UserStatus.BLOCKED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your wallet has been blocked by administration"
        )

    return user
