from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from typing import List, Optional
from uuid import UUID
import re

from db.session import get_db
from models.product import Product, ProductStatus
from models.category import Category
from models.user import User
from schemas.product import ProductCreate, ProductUpdate, ShowProduct
from core.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/products", tags=["Products"])

# ==================== ХЕЛПЕРЫ ====================
def generate_slug(title: str) -> str:
    """Генерирует slug из названия"""
    slug = title.lower().strip().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug

# ==================== ПУБЛИЧНЫЕ ЭНДПОИНТЫ ====================

@router.get("/", response_model=List[ShowProduct])
def get_products(
    category_id: Optional[UUID] = None,
    search: Optional[str] = None,
    status: Optional[ProductStatus] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_featured: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Получить список продуктов с фильтрацией
    """
    query = db.query(Product).options(joinedload(Product.category))
    
    # Только активные продукты для публичного доступа
    query = query.filter(Product.is_active == True)
    query = query.filter(Product.status == ProductStatus.PUBLISHED)
    
    # Фильтры
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(
            or_(
                Product.title.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
                Product.tags.contains([search])
            )
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    
    # Сортировка по новизне
    query = query.order_by(Product.created_at.desc())
    
    products = query.offset(offset).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ShowProduct)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получить продукт по ID
    """
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.seller)
    ).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Увеличиваем счётчик просмотров
    product.views_count += 1
    db.commit()
    
    return product


@router.get("/slug/{slug}", response_model=ShowProduct)
def get_product_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Получить продукт по slug
    """
    product = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.seller)
    ).filter(Product.slug == slug).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Увеличиваем счётчик просмотров
    product.views_count += 1
    db.commit()
    
    return product


# ==================== АДМИН-ЭНДПОИНТЫ ====================

@router.post("/", response_model=ShowProduct, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Создать продукт (только для админа)
    """
    # Генерируем slug, если не передан
    if not product_data.slug:
        product_data.slug = generate_slug(product_data.title)
    
    # Проверка уникальности slug
    existing = db.query(Product).filter(Product.slug == product_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this slug already exists"
        )
    
    # Проверка категории
    if product_data.category_id:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    product = Product(
        **product_data.model_dump(),
        seller_id=current_user.id
    )
    
    # Если продукт сразу публикуется
    if product.status == ProductStatus.PUBLISHED:
        product.published_at = func.now()
    
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ShowProduct)
def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Обновить продукт (только для админа)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = product_data.model_dump(exclude_unset=True)
    
    # ❌ Удаляем id, чтобы не обновлять его
    update_data.pop("id", None)
    
    # Проверка category_id
    if "category_id" in update_data and update_data["category_id"] is not None:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Проверка уникальности slug
    if "slug" in update_data and update_data["slug"] != product.slug:
        existing = db.query(Product).filter(
            Product.slug == update_data["slug"],
            Product.id != product_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this slug already exists"
            )
    
    # Если статус меняется на PUBLISHED
    if update_data.get("status") == ProductStatus.PUBLISHED and product.status != ProductStatus.PUBLISHED:
        update_data["published_at"] = func.now()
    
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Удалить продукт (только для админа)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    return None


@router.get("/admin/all", response_model=List[ShowProduct])
def get_all_products_admin(
    status: Optional[ProductStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Получить все продукты (для админа)
    """
    query = db.query(Product)
    
    if status:
        query = query.filter(Product.status == status)
    
    products = query.order_by(Product.created_at.desc()).offset(offset).limit(limit).all()
    return products