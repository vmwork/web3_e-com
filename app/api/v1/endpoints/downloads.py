from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from uuid import UUID
import secrets
import os

from db.session import get_db
from models.download_token import DownloadToken
from models.order_item import OrderItem
from models.order import OrderStatus
from models.user import User
from models.order import Order, OrderStatus 
from schemas.download_token import DownloadTokenCreate
from core.dependencies import get_current_user
from core.config import settings

router = APIRouter(prefix="/downloads", tags=["Downloads"])


@router.post("/tokens", status_code=status.HTTP_201_CREATED)
def create_download_token(
    order_item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать токен для скачивания файла
    """
    # Проверка: элемент заказа существует и принадлежит пользователю
    order_item = db.query(OrderItem).options(
        joinedload(OrderItem.order)
    ).filter(OrderItem.id == order_item_id).first()
    
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    
    # Проверка: заказ принадлежит пользователю
    if order_item.order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Проверка: заказ оплачен
    if order_item.order.status != OrderStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order not completed yet"
        )
    
    # Проверка: лимит скачиваний
    if order_item.download_count >= order_item.order.buyer.download_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Download limit exceeded"
        )
    
    # Генерируем токен
    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)
    
    download_token = DownloadToken(
        order_item_id=order_item_id,
        token=token_value,
        expires_at=expires_at,
        ip_address=None,  # Можно добавить из request
        user_agent=None    # Можно добавить из request
    )
    
    db.add(download_token)
    db.commit()
    db.refresh(download_token)
    
    return {
        "token": token_value,
        "expires_at": expires_at,
        "download_url": f"/api/v1/downloads/files/{token_value}"
    }


@router.get("/files/{token}")
def download_file(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Скачать файл по токену
    """
    # Проверка токена
    download_token = db.query(DownloadToken).filter(
        DownloadToken.token == token,
        DownloadToken.expires_at > datetime.now()
    ).first()
    
    if not download_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired token"
        )
    
    # Проверка: не использован ли уже
    if download_token.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already used"
        )
    
    # Получаем элемент заказа
    order_item = db.query(OrderItem).filter(
        OrderItem.id == download_token.order_item_id
    ).first()
    
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    
    # Проверяем существование файла
    file_path = order_item.product_file_path
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Обновляем токен
    download_token.used_at = datetime.now()
    
    # Увеличиваем счётчик скачиваний
    order_item.download_count += 1
    order_item.last_download_at = datetime.now()
    
    db.commit()
    
    # Возвращаем файл
    return FileResponse(
        path=file_path,
        filename=order_item.product_file_name,
        media_type="application/octet-stream"
    )


@router.get("/history", response_model=list)
def get_download_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить историю скачиваний
    """
    downloads = db.query(DownloadToken).join(
        OrderItem
    ).join(
        Order
    ).filter(
        Order.buyer_id == current_user.id,
        DownloadToken.used_at.isnot(None)
    ).order_by(
        DownloadToken.used_at.desc()
    ).all()
    
    result = []
    for dl in downloads:
        order_item = db.query(OrderItem).filter(
            OrderItem.id == dl.order_item_id
        ).first()
        result.append({
            "id": dl.id,
            "product_title": order_item.product_title if order_item else "Unknown",
            "downloaded_at": dl.used_at,
            "token": dl.token
        })
    
    return result