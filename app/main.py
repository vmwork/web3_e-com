import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os

from api.v1.endpoints import (
    auth, 
    users, 
    profiles, 
    user_configs,
    categories,
    products,
    orders,
    reviews,
    downloads
)
from core.config import settings  
from db.session import engine
from db.base import Base


def start_application() -> FastAPI:
    """Фабрика инициализации Enterprise Web3 API приложения"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.PROJECT_DESCRIPTION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        swagger_ui_parameters={
            "persistAuthorization": True,
        }
    )
    
    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Подключаем все роутеры
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(profiles.router, prefix="/api/v1")
    app.include_router(user_configs.router, prefix="/api/v1")
    app.include_router(categories.router, prefix="/api/v1")
    app.include_router(products.router, prefix="/api/v1")
    app.include_router(orders.router, prefix="/api/v1")
    app.include_router(reviews.router, prefix="/api/v1")
    app.include_router(downloads.router, prefix="/api/v1")
    
    # ============================================================
    # КАСТОМИЗАЦИЯ OPENAPI ДЛЯ OAuth2 (FORM LOGIN)
    # ============================================================
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # Добавляем схему OAuth2 (password flow)
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/api/v1/auth/token",
                        "scopes": {}
                    }
                }
            }
        }
        
        # Добавляем глобальную безопасность
        openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    # ============================================================
    
    # ✅ УБИРАЕМ ВЫЗОВ create_tables()
    
    return app


app = start_application()


@app.get("/", tags=["System"])
def root():
    return {
        "message": f"{settings.PROJECT_NAME} is running",
        "version": settings.PROJECT_VERSION,
        "docs": "/api/docs"
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )