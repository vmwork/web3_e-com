from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from models.user import User, UserStatus
from core.config import settings
from core.security import create_access_token, verify_wallet_signature
from schemas.user import ConnectRequest, AuthResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/connect", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def connect_wallet(
    request: ConnectRequest, 
    db: Session = Depends(get_db)
):
    """
    Аутентифікація користувача через криптографічний підпис гаманця Web3 (MetaMask/WalletConnect)
    """
    wallet_address = request.wallet_address
    message = request.message
    signature = request.signature

    # Честная, строгая криптографическая проверка подписи. Никаких обходов!
    if not verify_wallet_signature(wallet_address, message, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid wallet signature"
        )

    user = db.query(User).filter(User.wallet_address == wallet_address).first()
    
    if not user:
        user = User(wallet_address=wallet_address, wallet_type="EVM", status=UserStatus.PENDING)
        user.profile = Profile()
        user.config = UserConfig()
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        data={"sub": user.wallet_address},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
