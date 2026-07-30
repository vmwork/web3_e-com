import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Crypto Auth API"
    PROJECT_VERSION: str = "0.1.0"

    PROJECT_DESCRIPTION: str = (
        "### 🔗 Разработчик: Vladyslav | Senior Fullstack Developer\n"
        "👉 [Profile on freelancehunt : vmarwork](https://freelancehunt.com/freelancer/vmarwork.html)"
    )
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    class Config:
        # 🟢 Делаем путь к .env динамическим, чтобы он корректно подхватывался и локально, и внутри Docker / Render
        env_file = os.getenv("ENV_FILE_PATH", ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
