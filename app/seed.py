import os
import sys
import uuid
from db.session import SessionLocal
from models.user import User, UserStatus
from models.profile import Profile        
from models.user_config import UserConfig  

sys.path.insert(0, "/app/app")

def seed_crypto_admin():
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
            # Автоматически привязываем пустой профиль и дефолтный конфиг
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

if __name__ == "__main__":
    seed_crypto_admin()  # 🟢 Исправили имя вызываемой функции на правильное
