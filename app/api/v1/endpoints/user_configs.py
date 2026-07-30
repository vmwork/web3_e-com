from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db
from models.user import User
from models.user_config import UserConfig
from schemas.user_config import ShowUserConfig, UserConfigUpdate
from core.dependencies import get_current_user

router = APIRouter(prefix="/configs", tags=["User Configs"])

@router.get("/me", response_model=ShowUserConfig)
def get_my_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить системные настройки интерфейса для текущего кошелька"""
    config = db.query(UserConfig).filter(UserConfig.user_id == current_user.wallet_address).first()
    if not config:
        config = UserConfig(user_id=current_user.wallet_address)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.put("/me", response_model=ShowUserConfig)
def update_my_config(
    config_update: UserConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить настройки кошелька (тема, язык, уведомления, приватность)"""
    config = db.query(UserConfig).filter(UserConfig.user_id == current_user.wallet_address).first()
    if not config:
        config = UserConfig(user_id=current_user.wallet_address)
        db.add(config)
        
    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)
        
    db.commit()
    db.refresh(config)
    return config
