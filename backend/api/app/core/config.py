from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "星纹 AI 手相 API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:root@localhost:3306/xingwen"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 2  # 2 hours

    # AI Models (Token Proxy)
    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o"
    
    # Storage
    UPLOAD_DIR: str = "uploads"
    IMAGE_UPLOAD_DIR: str = "uploads/images"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
