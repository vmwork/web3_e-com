import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.user import User, UserStatus
from models.profile import Profile        
from models.user_config import UserConfig  
from models.category import Category
from models.product import Product, ProductStatus
from core.security import get_password_hash

sys.path.insert(0, "/app/app")


def seed_crypto_admin():
    """Создание суперадмина по кошельку"""
    db = SessionLocal()
    ADMIN_WALLET = os.getenv("ADMIN_WALLET_ADDRESS", "0x90F8bf6A479f320ced073E5743F257356671B414")
    
    try:
        admin = db.query(User).filter(User.wallet_address == ADMIN_WALLET).first()
        
        if not admin:
            print(f"🚀 СИД: Создание дефолтного суперадмина ({ADMIN_WALLET})...")
            new_admin = User(
                wallet_address=ADMIN_WALLET,
                wallet_type="EVM",
                status=UserStatus.ACTIVE,
                role="admin",
                display_name="Crypto Admin",
                has_paid_entrance=True
            )
            new_admin.profile = Profile()
            new_admin.config = UserConfig()
            
            db.add(new_admin)
            db.commit()
            print("🟢 СИД: Суперадмин кошелька вместе с профилем успешно создан!")
            
        elif admin.role != "admin" or admin.status != UserStatus.ACTIVE:
            print(f"🔄 СИД: Кошелек {ADMIN_WALLET} существует, но не имеет прав админа. Обновление...")
            admin.role = "admin"
            admin.status = UserStatus.ACTIVE
            db.commit()
            print("🟢 СИД: Права суперадмина успешно выданы существующему кошельку!")
            
        else:
            print("ℹ️ СИД: Суперадмин кошелька уже существует в базе и имеет полные права.")
            
    except Exception as e:
        print(f"❌ СИД: Ошибка при обработке крипто-админа: {e}")
    finally:
        db.close()


def seed_test_users():
    """Создание тестовых пользователей для разработки"""
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли тестовые пользователи
        existing = db.query(User).filter(User.email.in_([
            "admin@example.com",
            "user@example.com",
            "seller@example.com"
        ])).first()
        
        if existing:
            print("ℹ️ СИД: Тестовые пользователи уже существуют, пропускаем...")
            return
        
        # Админ (email)
        admin = User(
            wallet_address="admin_email_wallet",
            wallet_type="EMAIL",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            is_email_verified=True,
            display_name="Admin User",
            status=UserStatus.ACTIVE,
            role="admin",
            has_paid_entrance=True
        )
        admin.profile = Profile(bio="System Administrator")
        admin.config = UserConfig(theme="dark", language="en")
        db.add(admin)
        
        # Обычный пользователь
        user = User(
            wallet_address="user_email_wallet",
            wallet_type="EMAIL",
            email="user@example.com",
            hashed_password=get_password_hash("user123"),
            is_email_verified=True,
            display_name="Test User",
            status=UserStatus.ACTIVE,
            role="user",
            has_paid_entrance=True
        )
        user.profile = Profile(
            bio="Test user for development",
            social_links={"twitter": "https://twitter.com/testuser"}
        )
        user.config = UserConfig(theme="light", language="en")
        db.add(user)
        
        db.commit()
        print("✅ СИД: Тестовые пользователи созданы:")
        print("   - admin@example.com / admin123 (admin)")
        print("   - user@example.com / user123 (user)")
        
    except Exception as e:
        print(f"❌ СИД: Ошибка при создании тестовых пользователей: {e}")
        db.rollback()
    finally:
        db.close()


def seed_categories():
    """Создание начальных категорий"""
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли категории
        existing = db.query(Category).first()
        if existing:
            print("ℹ️ СИД: Категории уже существуют, пропускаем...")
            return
        
        categories = [
            {"name": "E-books", "slug": "e-books", "icon": "📚", "color": "#4A90D9", "sort_order": 1},
            {"name": "Software", "slug": "software", "icon": "💻", "color": "#27AE60", "sort_order": 2},
            {"name": "Templates", "slug": "templates", "icon": "📄", "color": "#F39C12", "sort_order": 3},
            {"name": "Design Assets", "slug": "design-assets", "icon": "🎨", "color": "#E74C3C", "sort_order": 4},
            {"name": "Audio & Music", "slug": "audio-music", "icon": "🎵", "color": "#9B59B6", "sort_order": 5},
            {"name": "Video & Animation", "slug": "video-animation", "icon": "🎬", "color": "#1ABC9C", "sort_order": 6},
            {"name": "WordPress Themes", "slug": "wordpress-themes", "icon": "🖥️", "color": "#21759B", "sort_order": 7},
            {"name": "Plugins & Extensions", "slug": "plugins-extensions", "icon": "🔌", "color": "#3498DB", "sort_order": 8},
        ]
        
        for cat_data in categories:
            category = Category(**cat_data, is_active=True)
            db.add(category)
        
        db.commit()
        print(f"✅ СИД: Создано {len(categories)} категорий")
        
    except Exception as e:
        print(f"❌ СИД: Ошибка при создании категорий: {e}")
        db.rollback()
    finally:
        db.close()


def seed_test_products():
    """Создание тестовых продуктов (для разработки)"""
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли продукты
        existing = db.query(Product).first()
        if existing:
            print("ℹ️ СИД: Продукты уже существуют, пропускаем...")
            return
        
        # Получаем админа и категории
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            print("⚠️ СИД: Админ не найден, пропускаем создание продуктов...")
            return
        
        categories = db.query(Category).all()
        if not categories:
            print("⚠️ СИД: Категории не найдены, пропускаем создание продуктов...")
            return
        
        # Создаём тестовые продукты
        products = [
            {
                "title": "Mastering Python: Advanced Guide",
                "description": "Complete guide to advanced Python programming with real-world examples",
                "price": 29.99,
                "file_path": "/app/uploads/python_guide.pdf",
                "file_name": "python_guide.pdf",
                "file_mime_type": "application/pdf",
                "download_limit": 5,
            },
            {
                "title": "React.js Starter Template",
                "description": "Production-ready React.js template with TypeScript and Tailwind CSS",
                "price": 19.99,
                "file_path": "/app/uploads/react_template.zip",
                "file_name": "react_template.zip",
                "file_mime_type": "application/zip",
                "download_limit": 10,
            },
            {
                "title": "UI Design System Kit",
                "description": "Complete UI design system with Figma components and design tokens",
                "price": 39.99,
                "file_path": "/app/uploads/ui_kit.fig",
                "file_name": "ui_kit.fig",
                "file_mime_type": "application/octet-stream",
                "download_limit": 3,
            },
        ]
        
        for idx, prod_data in enumerate(products):
            category = categories[idx % len(categories)]
            product = Product(
                seller_id=admin.id,
                title=prod_data["title"],
                description=prod_data["description"],
                price=prod_data["price"],
                currency="USD",
                category_id=category.id,
                file_path=prod_data["file_path"],
                file_name=prod_data["file_name"],
                file_mime_type=prod_data["file_mime_type"],
                download_limit=prod_data["download_limit"],
                status=ProductStatus.PUBLISHED,
                is_active=True,
                is_featured=idx == 0,  # Первый продукт - featured
                preview_images=["https://via.placeholder.com/300x200"],
                tags=["python", "react", "design"],
                rating_avg=4.5,
                rating_count=10,
                published_at=datetime.now()
            )
            db.add(product)
        
        db.commit()
        print(f"✅ СИД: Создано {len(products)} тестовых продуктов")
        
    except Exception as e:
        print(f"❌ СИД: Ошибка при создании продуктов: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Главная функция сида"""
    print("=" * 60)
    print("🌱 ЗАПУСК НАПОЛНЕНИЯ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    seed_crypto_admin()
    seed_test_users()
    seed_categories()
    seed_test_products()
    
    print("=" * 60)
    print("✅ НАПОЛНЕНИЕ БАЗЫ ДАННЫХ ЗАВЕРШЕНО")
    print("=" * 60)


if __name__ == "__main__":
    main()