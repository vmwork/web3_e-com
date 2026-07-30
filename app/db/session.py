from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from db.base import Base 
from models.user import User
from models.profile import Profile
from models.user_config import UserConfig

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

Base.__table_args__ = {"extend_existing": True}

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
