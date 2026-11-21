"""
Application Settings & Configuration Module
Loads environment variables from .env using Pydantic Settings.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project metadata
    PROJECT_NAME: str = "AI Knowledge Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security & JWT Tokens
    APP_SECRET_KEY: str = "change-this-to-a-very-secure-random-secret-key-32-chars-min"
    JWT_SECRET_KEY: str = "change-this-jwt-secret-key-to-something-secure-for-tokens"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS settings
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_HOSTS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/knowledge_assistant"
    TEST_DATABASE_URL: str = "sqlite:///./test.db"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # S3 / MinIO Object Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "knowledge-assistant-docs"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False
    LOCAL_STORAGE_DIR: str = "./storage_data"

    # OpenAI & AI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # RAG Settings
    RAG_TOP_K_CHUNKS: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.3
    RAG_CHUNK_SIZE_TOKENS: int = 600
    RAG_CHUNK_OVERLAP_TOKENS: int = 100
    MAX_UPLOAD_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def cors_origins(self) -> List[str]:
        origins = [
            self.FRONTEND_URL,
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:4173",   # vite preview
            "http://127.0.0.1:4173",
        ]
        return origins


# Global singleton instance
settings = Settings()
