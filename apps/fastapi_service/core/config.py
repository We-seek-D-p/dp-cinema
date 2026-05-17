from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"

    S3_INTERNAL_ENDPOINT: str
    S3_PUBLIC_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str

    @property
    def s3_endpoint(self) -> str:
        """Для совместимости со старым кодом возвращает INTERNAL endpoint"""
        return self.S3_INTERNAL_ENDPOINT

    DJANGO_API_URL: str = "http://localhost:8000"
    FASTAPI_SERVICE_URL: str = "http://localhost:8001"
    INTERNAL_SERVICE_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator(
        "REDIS_URL",
        "S3_INTERNAL_ENDPOINT",
        "S3_PUBLIC_ENDPOINT",
        "S3_ACCESS_KEY",
        "S3_SECRET_KEY",
        "S3_BUCKET",
        "DJANGO_API_URL",
        "INTERNAL_SERVICE_TOKEN",
    )
    @classmethod
    def validate_non_empty(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field cannot be empty: {info.field_name}")
        return v


settings = Settings()
