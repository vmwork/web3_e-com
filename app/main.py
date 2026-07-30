import uvicorn
from fastapi import FastAPI
from api.v1.endpoints import auth, users, profiles, user_configs  
from core.config import settings  
from db.session import engine
from db.base import Base


def create_tables():
    """Принудительная инициализация структуры таблиц в PostgreSQL"""
    Base.metadata.create_all(bind=engine)


def start_application() -> FastAPI:
    """Фабрика инициализации Enterprise Web3 API приложения"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.PROJECT_DESCRIPTION,
    )
    
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(profiles.router, prefix="/api/v1")        
    app.include_router(user_configs.router, prefix="/api/v1") 
    
    create_tables()
    
    return app


app = start_application()


@app.get("/", tags=["System"])
def root():
    return {"message": f"{settings.PROJECT_NAME} is running"}


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
