from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import secrets
import string

from db.session import get_db
from models.order import Order, OrderStatus
from models.order_item import OrderItem
from models.product import Product
from models.user import User
from schemas.order import OrderCreate, OrderUpdate, ShowOrder
from schemas.order_item import OrderItemCreate
from core.dependencies import get_current_user, get_current_admin_user
from models.product import Product, ProductStatus
router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_order_number() -> str:
    """Генерация уникального номера заказа"""
    prefix = "ORD"
    timestamp = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"{prefix}-{timestamp}-{random_part}"


@router.get("/", response_model=List[ShowOrder])
def get_my_orders(
    status: Optional[OrderStatus] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список заказов текущего пользователя
    """
    query = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.buyer_id == current_user.id)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=ShowOrder)
def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить заказ по ID
    """
    order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Проверка: пользователь должен быть покупателем или админом
    if order.buyer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return order


@router.post("/", response_model=ShowOrder, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый заказ
    """
    # Проверка: есть ли у пользователя кошелёк
    if not current_user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a wallet. Please connect your wallet first."
        )
    
    # Проверка: товары должны существовать
    total_subtotal = 0
    items_data = []
    
    for item in order_data.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.is_active == True,
            Product.status == ProductStatus.PUBLISHED
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found or not available"
            )
        
        subtotal = product.price * item.quantity
        total_subtotal += subtotal
        
        items_data.append({
            "product_id": product.id,
            "product_title": product.title,
            "product_price": product.price,
            "product_file_path": product.file_path,
            "product_file_name": product.file_name,
            "quantity": item.quantity,
            "subtotal": subtotal
        })
    
    # Создаём заказ
    order = Order(
        order_number=generate_order_number(),
        buyer_id=current_user.id,
        subtotal=total_subtotal,
        tax_amount=order_data.tax_amount or 0,
        discount_amount=order_data.discount_amount or 0,
        total_amount=total_subtotal + (order_data.tax_amount or 0) - (order_data.discount_amount or 0),
        currency=order_data.currency or "USD",
        status=OrderStatus.PENDING,
        buyer_email=current_user.email or order_data.buyer_email,
        buyer_wallet=current_user.wallet_address,
        payment_method=order_data.payment_method,
        payment_currency=order_data.payment_currency,
        payment_amount=order_data.payment_amount
    )
    
    db.add(order)
    db.flush()  # 👈 Чтобы получить order.id
    
    # Создаём элементы заказа
    for item_data in items_data:
        order_item = OrderItem(
            order_id=order.id,  # 👈 order_id берётся из созданного заказа
            **item_data
        )
        db.add(order_item)
        
        # Увеличиваем счётчик покупок у продукта
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        if product:
            product.purchases_count += 1
    
    db.commit()
    db.refresh(order)
    
    return order
    
    # Создаём заказ
    order = Order(
        order_number=generate_order_number(),
        buyer_id=current_user.id,
        subtotal=total_subtotal,
        tax_amount=order_data.tax_amount or 0,
        discount_amount=order_data.discount_amount or 0,
        total_amount=total_subtotal + (order_data.tax_amount or 0) - (order_data.discount_amount or 0),
        currency=order_data.currency or "USD",
        status=OrderStatus.PENDING,
        buyer_email=current_user.email or order_data.buyer_email,
        buyer_wallet=current_user.wallet_address,
        payment_method=order_data.payment_method,
        payment_currency=order_data.payment_currency,
        payment_amount=order_data.payment_amount
    )
    
    db.add(order)
    db.flush()  # Чтобы получить order.id
    
    # Создаём элементы заказа
    for item_data in items_data:
        order_item = OrderItem(
            order_id=order.id,
            **item_data
        )
        db.add(order_item)
        
        # Увеличиваем счётчик покупок у продукта
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        if product:
            product.purchases_count += 1
    
    db.commit()
    db.refresh(order)
    
    return order


@router.put("/{order_id}", response_model=ShowOrder)
def update_order_status(
    order_id: UUID,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить статус заказа (покупатель может отменить, админ - всё)
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Проверка прав
    is_admin = current_user.role == "admin"
    is_buyer = order.buyer_id == current_user.id
    
    if not is_admin and not is_buyer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Покупатель может только отменить заказ
    if is_buyer and not is_admin:
        if order_update.status not in [OrderStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can only cancel your order"
            )
        if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel order in current status"
            )
    
    # Обновляем статус
    if order_update.status == OrderStatus.PAID:
        order.paid_at = func.now()
    elif order_update.status == OrderStatus.COMPLETED:
        order.completed_at = func.now()
    elif order_update.status == OrderStatus.CANCELLED:
        # Возвращаем товары
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.purchases_count -= 1
    
    order.status = order_update.status
    db.commit()
    db.refresh(order)
    
    return order


# ==================== АДМИН-ЭНДПОИНТЫ ====================

@router.get("/admin/all", response_model=List[ShowOrder])
def get_all_orders_admin(
    status: Optional[OrderStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Получить все заказы (для админа)
    """
    query = db.query(Order).options(joinedload(Order.items))
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    return orders